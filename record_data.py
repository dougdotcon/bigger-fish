import os

if "DISPLAY" not in os.environ:
    # Inicia o selenium no display principal se o experimento for iniciado via SSH
    os.environ["DISPLAY"] = ":0"

from enum import Enum

import argparse
import ctypes
import json
import logging
import math
import os
import pickle
import queue
import shutil
import signal
import subprocess
import sys
import threading
import time

from drivers import LinksDriver, RemoteDriver, SafariDriver

from flask import Flask, send_from_directory
from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, TimeoutException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from urllib3.exceptions import MaxRetryError, ProtocolError

import pandas as pd


class Browser(Enum):
    CHROME = "chrome"
    CHROME_HEADLESS = "chrome_headless"
    FIREFOX = "firefox"
    SAFARI = "safari"
    LINKS = "links"
    REMOTE = "remote"
    TOR_BROWSER = "tor_browser"

    def __str__(self):
        return self.name.lower()

    def get_new_tab_url(self):
        if self == Browser.CHROME or self == Browser.CHROME_HEADLESS:
            return "chrome://new-tab-page"
        elif self == Browser.FIREFOX:
            return "about:home"
        elif self == Browser.SAFARI:
            return "favorites://"
        elif self == Browser.LINKS:
            raise NotImplementedError()
        elif self == Browser.REMOTE:
            return "biggerfish://new-tab"
        elif self == Browser.TOR_BROWSER:
            return "about:blank"


parser = argparse.ArgumentParser(
    description="Automatiza a coleta de traços de CPU baseados em navegador."
)
parser.add_argument(
    "--browser",
    type=Browser,
    choices=list(Browser),
    default="chrome",
    help="O navegador a ser usado para o processo vítima.",
)
parser.add_argument("--num_runs", type=int, default=100)
parser.add_argument(
    "--attacker_type",
    type=str,
    choices=["javascript", "javascript_cache", "counter", "ebpf"],
    default="javascript",
)
parser.add_argument(
    "--javascript_attacker_type",
    type=str,
    choices=["ours", "ours_with_timer_countermeasure", "cache"],
    default="ours",
)
parser.add_argument(
    "--trace_length",
    type=int,
    default=15,
    help="A duração de cada traço gravado, em segundos.",
)
parser.add_argument(
    "--sites_list",
    type=str,
    default="alexa100",
    help="A lista de sites a ser usada. Se usar os n principais sites do Alexa EUA, deve ser alexan, onde n >= 1.",
)
parser.add_argument(
    "--receiver_ip",
    type=str,
    default="0.0.0.0",
    help="O endereço do receptor, se estiver usando um.",
)
parser.add_argument(
    "--receiver_port",
    type=int,
    default=1234,
    help="A porta do receptor, se estiver usando um.",
)
parser.add_argument(
    "--out_directory", type=str, default="data", help="O nome do diretório de saída."
)
parser.add_argument(
    "--timer_resolution",
    type=float,
    default=None,
    help="Resolução do temporizador durante ataques de contador. Ex: se definido como 0.001, arredonda para o milissegundo mais próximo.",
)
parser.add_argument(
    "--enable_timer_jitter",
    type=bool,
    default=False,
    help="True se quisermos habilitar o algoritmo de jitter do Chrome durante ataques de contador.",
)
parser.add_argument(
    "--twilio_interval",
    type=float,
    default=0.1,
    help="Intervalo para enviar atualizações com Twilio. Ex: se definido como 0.1, enviará uma mensagem cada vez que mais 10%% dos traços forem coletados. Defina como 0 para desabilitar.",
)
parser.add_argument(
    "--overwrite",
    type=bool,
    default=False,
    help="True se quisermos sobrescrever o diretório de saída.",
)
parser.add_argument(
    "--disable_chrome_sandbox",
    type=bool,
    default=False,
    help="True se quisermos desabilitar a sandbox do Chrome. O navegador deve ser chrome ou chrome_headless.",
)
parser.add_argument(
    "--tor_browser_path",
    type=str,
    help="Caminho para o pacote do Tor Browser. O navegador deve ser tor_browser.",
)
parser.add_argument(
    "--tor_onion_address",
    type=str,
    help="Endereço onion para acessar o atacante via Tor.",
)
parser.add_argument(
    "--enable_cache_countermeasure",
    type=bool,
    default=False,
    help="True se quisermos habilitar a extensão de contramedida de cache do Chrome.",
)
parser.add_argument(
    "--enable_interrupts_countermeasure",
    type=bool,
    default=False,
    help="True se quisermos habilitar a extensão de contramedida de interrupções do Chrome.",
)
parser.add_argument(
    "--chrome_binary_path",
    type=str,
    default=None,
    help="Caminho para um diretório contendo os binários do chrome e chromedriver, se desejado.",
)
parser.add_argument(
    "--ebpf_ns_threshold",
    type=int,
    default=500,
    help="Duração mínima do intervalo para registrar interrupções com a ferramenta eBPF.",
)
opts = parser.parse_args()

if opts.sites_list == "open_world" and opts.num_runs != 1:
    print("Se sites_list = open_world, num_runs deve ser igual a 1.")
    sys.exit(1)

if (
    opts.disable_chrome_sandbox
    and opts.browser != Browser.CHROME
    and opts.browser != Browser.CHROME_HEADLESS
):
    print(
        "Você não pode definir disable_chrome_sandbox como true a menos que o navegador seja chrome ou chrome_headless."
    )
    sys.exit(1)

if opts.browser == Browser.REMOTE and (
    opts.receiver_ip is None or opts.receiver_port is None
):
    print("Se o navegador for remote, deve passar receiver_ip e receiver_port.")
    sys.exit(1)

if opts.attacker_type == "ebpf":
    # Obtém acesso root antes de executar o resto do script
    subprocess.call(["sudo", "whoami"], stdout=subprocess.PIPE)

if (
    opts.tor_browser_path is not None or opts.tor_onion_address is not None
) and opts.browser != Browser.TOR_BROWSER:
    print(
        "Você não pode definir tor_browser_path ou tor_onion_address sem definir o navegador como tor_browser."
    )
    sys.exit(1)

if opts.browser == Browser.TOR_BROWSER and (
    opts.tor_browser_path is None or opts.tor_onion_address is None
):
    print(
        "Se o navegador for tor_browser, tor_browser_path e tor_onion_address devem ser definidos."
    )
    sys.exit(1)

if opts.enable_timer_jitter and opts.timer_resolution is None:
    print("Se enable_timer_jitter for true, timer_resolution deve ser definido.")
    sys.exit(1)

if opts.timer_resolution is not None and not os.path.exists(
    os.path.join("lib", "libtimer.so")
):
    print("libtimer.so precisa ser compilado. Execute:")
    print("cc -fPIC -shared -o lib/libtimer.so lib/timer.c")
    sys.exit(1)


def confirm(prompt):
    response = input(f"{prompt} [s/N] ")

    if "s" not in response.lower():
        sys.exit(1)


remote_driver = None

if opts.timer_resolution is not None:
    c_lib = ctypes.CDLL(os.path.join(os.getcwd(), "lib", "libtimer.so"))
    c_lib.configure_timer.argtypes = [ctypes.c_double, ctypes.c_bool]
    c_lib.configure_timer(opts.timer_resolution, opts.enable_timer_jitter)
    c_lib.timer.restype = ctypes.c_double


def get_attacker_url():
    if opts.browser == Browser.TOR_BROWSER:
        if not opts.tor_onion_address.startswith("http://"):
            return f"http://{opts.tor_onion_address}"
        return opts.tor_onion_address

    if opts.browser == Browser.REMOTE:
        return "http://localhost:5000"

    return "file://" + os.path.abspath("attacker/index.html")


def get_driver(browser):
    if browser == Browser.CHROME or browser == Browser.CHROME_HEADLESS:
        options = Options()

        if browser == Browser.CHROME_HEADLESS:
            options.add_argument("--headless")

        if opts.disable_chrome_sandbox:
            options.add_argument("--no-sandbox")

        if opts.enable_cache_countermeasure:
            options.add_extension("extensions/cache.crx")

        if opts.enable_interrupts_countermeasure:
            options.add_extension("extensions/interrupts.crx")

        if opts.chrome_binary_path is not None:
            options.binary_location = os.path.join(
                opts.chrome_binary_path, "chrome"
            )

            driver = webdriver.Chrome(
                executable_path=os.path.join(
                    opts.chrome_binary_path, "chromedriver"
                ),
                options=options,
            )
        else:
            driver = webdriver.Chrome(options=options)

        driver.set_page_load_timeout(15)
        return driver
    elif browser == Browser.FIREFOX:
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(15)
        return driver
    elif browser == Browser.SAFARI:
        return SafariDriver(get_attacker_url())
    elif browser == Browser.LINKS:
        return LinksDriver()
    elif browser == Browser.REMOTE:
        return RemoteDriver(opts.receiver_ip, opts.receiver_port)
    elif browser == Browser.TOR_BROWSER:
        from tbselenium.tbdriver import TorBrowserDriver

        driver = TorBrowserDriver(
            opts.tor_browser_path,
            tbb_logfile_path="tbdriver.log",
            tor_cfg=lambda tor: tor.set_control_port_password("password"),
        )

        driver.set_page_load_timeout(15)
        return driver


# Make sure existing processes aren't running
procs = subprocess.check_output(["ps", "aux"]).decode("utf-8").split("\n")

for term in ["python", "chrome", "safaridriver"]:
    conflicts = []

    for p in procs:
        if (
            len(p) < 2
            or not p.split()[1].isnumeric()
            or os.getpid() == int(p.split()[1])
        ):
            continue

        if term.lower() in p.lower():
            conflicts.append(p)

    if len(conflicts) > 0:
        print()
        print("Processes")
        print("=========")
        print("\n".join(conflicts))
        confirm(
            f"Potentially conflicting {term} processes are currently running. OK to continue?"
        )

# Double check that we're not overwriting old data
if not opts.overwrite and os.path.exists(opts.out_directory):
    print(
        f"WARNING: Data already exists at {opts.out_directory}. What do you want to do?"
    )
    res = input("[A]ppend [C]ancel [O]verwrite ").lower()

    if res == "a":
        pass
    elif res == "o":
        confirm(
            f"WARNING: You're about to overwrite {opts.out_directory}. Are you sure?"
        )
        shutil.rmtree(opts.out_directory)
    else:
        sys.exit(1)
elif opts.overwrite:
    shutil.rmtree(opts.out_directory)

if not os.path.exists(opts.out_directory):
    os.mkdir(opts.out_directory)

# Optionally set up SMS notifications
using_twilio = False

if opts.twilio_interval != 0:
    if os.path.exists("twilio.json"):
        from twilio.rest import Client

        twilio_data = json.loads(open("twilio.json").read())
        twilio_client = Client(twilio_data["account_sid"], twilio_data["auth_token"])
        using_twilio = True
    else:
        print(
            "WARNING: No twilio.json file found, but twilio_interval > 0. Continuing anyway."
        )


def send_notification(message):
    if opts.twilio_interval == 0:
        return

    try:
        from twilio.rest import Client

        with open("twilio_config.json", "r") as f:
            config = json.loads(f.read())

        client = Client(config["account_sid"], config["auth_token"])
        client.messages.create(
            body=message,
            from_=config["from_number"],
            to=config["to_number"],
        )
    except:
        print("Falha ao enviar notificação por SMS")


app = Flask(__name__, static_folder="attacker")


@app.route("/")
def root():
    return send_from_directory("attacker", "index.html")


@app.route("/<path:path>")
def static_dir(path):
    return send_from_directory("attacker", path)


def create_browser():
    global remote_driver

    if remote_driver is not None:
        remote_driver.quit()

    remote_driver = get_driver(opts.browser)


def get_time():
    if opts.timer_resolution is not None:
        return c_lib.timer()
    else:
        return time.time()


def collect_data(q):
    # Aguarda até que o navegador esteja pronto
    while True:
        try:
            remote_driver.execute_script("window.recording")
            break
        except:
            time.sleep(0.1)

    # Aguarda até que o navegador comece a gravar
    while True:
        try:
            if remote_driver.execute_script("return window.recording"):
                break
        except:
            time.sleep(0.1)

    # Coleta dados
    T = []
    start = get_time()

    while True:
        t = get_time()

        if t - start >= opts.trace_length:
            break

        if opts.attacker_type == "counter":
            counter = 0

            while get_time() - t < 0.005:
                counter += 1

            T.append(counter)
        elif opts.attacker_type == "ebpf":
            time.sleep(0.005)

    if opts.attacker_type == "counter":
        q.put(T)
    elif opts.attacker_type == "ebpf":
        q.put(None)


def record_trace(url):
    if opts.attacker_type == "javascript":
        # Configura o navegador
        remote_driver.execute_script(
            f"window.trace_length = {opts.trace_length * 1000}"
        )
        remote_driver.execute_script("window.using_automation_script = true")

        # Inicia a gravação
        remote_driver.execute_script(
            f"collectTrace('{opts.javascript_attacker_type}')"
        )

        # Carrega a página
        remote_driver.get(url)

        # Aguarda até que a gravação termine
        while True:
            try:
                if not remote_driver.execute_script("return window.recording"):
                    break
            except:
                time.sleep(0.1)

        # Obtém os dados
        return remote_driver.execute_script("return window.traces[0]")
    else:
        q = queue.Queue()
        t = threading.Thread(target=collect_data, args=(q,))
        t.start()

        # Carrega a página
        remote_driver.get(url)

        t.join()
        return q.get()


recording = True


def signal_handler(sig, frame):
    print("\nLimpando...")

    if remote_driver is not None:
        remote_driver.quit()

    if opts.attacker_type == "ebpf":
        subprocess.call(["sudo", "pkill", "ebpf"])

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
using_custom_site = False


if opts.sites_list.startswith("alexa"):
    n = int(opts.sites_list.replace("alexa", ""))

    if n > 100:
        print("For sites_list, n must be less than or equal to 100.")
        sys.exit(1)

    domains = pd.read_csv(os.path.join("sites", "closed_world.csv"))["domain"].tolist()
    domains = [f"https://{x}" if "http://" not in x else x for x in domains]
    domains = domains[:n]
elif opts.sites_list == "open_world":
    domains = pd.read_csv(os.path.join("sites", "open_world.csv"))["domain"].tolist()
    domains = [f"https://{x}" if "http://" not in x else x for x in domains]
else:
    domains = opts.sites_list.split(",")
    domains = [f"https://{x}" if "http://" not in x else x for x in domains]
    using_custom_site = True


def should_skip(domain):
    if domain.startswith("!"):
        return True

    if "." not in domain:
        domain = f"{domain}.com"

    try:
        remote_driver.get(f"http://{domain}")
        return False
    except TimeoutException:
        print(f"Tempo esgotado ao carregar {domain}")
        return True
    except (InvalidSessionIdException, MaxRetryError, ProtocolError):
        print(f"Erro ao carregar {domain}")
        create_browser()
        return True
    except:
        print(f"Erro desconhecido ao carregar {domain}")
        return True


def run(domain, update_fn=None):
    if domain.startswith("!"):
        domain = domain[1:]

    if "." not in domain:
        domain = f"{domain}.com"

    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = f"http://{domain}"

    traces = []
    labels = []

    for i in range(opts.num_runs):
        try:
            trace = record_trace(domain)

            if trace is not None:
                traces.append(trace)
                labels.append(domain)

                if update_fn is not None:
                    update_fn()
        except TimeoutException:
            print(f"Tempo esgotado ao carregar {domain}")
            create_browser()
        except (InvalidSessionIdException, MaxRetryError, ProtocolError):
            print(f"Erro ao carregar {domain}")
            create_browser()
        except:
            print(f"Erro desconhecido ao carregar {domain}")
            create_browser()

    return traces, labels


browser = None
total_traces = opts.num_runs * len(domains)

with tqdm(total=total_traces) as pbar:
    if using_twilio:
        notify_interval = opts.twilio_interval * total_traces
        last_notification = 0

    traces_collected = 0

    def post_trace_collection():
        global traces_collected, notify_interval, last_notification

        pbar.update(1)
        traces_collected += 1

        if using_twilio and traces_collected >= last_notification + notify_interval:
            send_notification(
                f"{twilio_data['name']} is done with {traces_collected / total_traces * 100:.0f}% of its current job!"
            )
            last_notification = traces_collected

    for i, domain in enumerate(domains):
        if not recording:
            break
        elif should_skip(domain):
            continue

        if (
            opts.browser == Browser.SAFARI
            and opts.attacker_type == "javascript"
            and browser is not None
        ):
            # Don't create a new browser in this case -- we will open a new
            # window instead due to limitations in safaridriver.
            pass
        else:
            browser = create_browser()

            if opts.browser == Browser.SAFARI:
                attacker_browser = browser

        success = run(domain, update_fn=post_trace_collection)

        if success:
            if opts.sites_list == "open_world" and traces_collected == 5000:
                break

            pbar.n = (i + 1) * opts.num_runs
            pbar.refresh()

        browser.quit()

if opts.attacker_type == "javascript":
    attacker_browser.quit()

if opts.sites_list == "open_world":
    browser.quit()

if opts.browser == Browser.SAFARI:
    try:
        browser.driver.quit()
    except:
        os.system("killall Safari")

if using_twilio:
    send_notification(f"{twilio_data['name']} is done with its job!")

if __name__ == "__main__":
    if os.path.exists(opts.out_directory):
        if opts.overwrite:
            shutil.rmtree(opts.out_directory)
        else:
            confirm(
                f"O diretório {opts.out_directory} já existe. Deseja sobrescrevê-lo?"
            )
            shutil.rmtree(opts.out_directory)

    os.makedirs(opts.out_directory)

    if opts.sites_list == "open_world":
        df = pd.read_csv("sites/open_world.csv")
        domains = df["domain"].tolist()
    else:
        if opts.sites_list.startswith("alexa"):
            n = int(opts.sites_list[5:])
            domains = alexa_domains[:n]
        else:
            df = pd.read_csv(f"sites/{opts.sites_list}.csv")
            domains = df["domain"].tolist()

    if opts.attacker_type == "ebpf":
        subprocess.Popen(
            [
                "sudo",
                "ebpf/target/release/ebpf",
                "--ns-threshold",
                str(opts.ebpf_ns_threshold),
            ]
        )

    if opts.browser == Browser.REMOTE:
        threading.Thread(target=app.run).start()

    create_browser()
    remote_driver.get(get_attacker_url())

    def post_trace_collection():
        if opts.attacker_type == "ebpf":
            subprocess.call(["sudo", "pkill", "ebpf"])

        if remote_driver is not None:
            remote_driver.quit()

    traces = []
    labels = []

    for i, domain in enumerate(tqdm(domains)):
        if should_skip(domain):
            continue

        traces_i, labels_i = run(domain, lambda: send_notification(
            f"Coletados {i + 1}/{len(domains)} sites"
        ))

        if len(traces_i) > 0:
            with open(os.path.join(opts.out_directory, f"{i}.pkl"), "wb") as f:
                pickle.dump([traces_i, labels_i], f)

    post_trace_collection()
