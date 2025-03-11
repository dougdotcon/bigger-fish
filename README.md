# 🎯 Bigger Fish Attack Framework
<div align="center">

```ascii
  _____ _                    _____ _     _     
 |  ___(_)_ __   __ _  ___ |  ___(_)___| |__  
 | |_  | | '_ \ / _` |/ _ \| |_  | / __| '_ \ 
 |  _| | | | | | (_| |  __/|  _| | \__ \ | | |
 |_|   |_|_| |_|\__, |\___||_|   |_|___/_| |_|
                |___/                          
```

### 🎣 Sempre Existe um Peixe Maior
*Um framework para ataques de canal lateral baseados em machine learning*

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Licença MIT](https://img.shields.io/badge/Licença-MIT-green.svg?style=for-the-badge)](LICENSE.md)
[![Pesquisa de Segurança](https://img.shields.io/badge/⚠️%20Pesquisa-Segurança-red.svg?style=for-the-badge)](https://doi.org/10.1145/3470496.3527416)

---

**[📖 Documentação](#-sobre-o-projeto)** • 
**[🚀 Começando](#-começando)** • 
**[🧪 Experimentos](#-experimentos)** • 
**[❓ FAQ](#-perguntas-frequentes)** • 
**[📄 Licença](#-licença)**

---

</div>

> 🔐 **Aviso de Segurança**: Este é um projeto de pesquisa que demonstra como sites podem ser identificados através de ataques de canal lateral, mesmo com proteções como VPNs e navegação privada. Use apenas para fins educacionais e de pesquisa!

> 🎯 **Precisão do Ataque**: Consegue identificar sites com até **87.3%** de precisão apenas observando o comportamento da CPU!

## 📋 Sobre o Projeto

Este projeto demonstra **ataques de canal lateral (side-channel)** que usam aprendizado de máquina para identificar quais sites um usuário está visitando, mesmo sem ter acesso direto ao navegador. É como "espionar" a atividade do navegador apenas observando o comportamento do processador!

### 🔍 O que são ataques de canal lateral?

Ataques de canal lateral exploram informações vazadas durante a execução de um sistema, em vez de atacar diretamente suas vulnerabilidades. Neste projeto, demonstramos como:

- **Contadores de CPU**: Podemos medir o desempenho do processador enquanto um site é carregado
- **Padrões de tempo**: Diferentes sites geram padrões únicos de uso da CPU
- **Aprendizado de máquina**: Usamos esses padrões para "adivinhar" qual site está sendo visitado

### 🛡️ Por que isso é importante?

Estes ataques funcionam mesmo com proteções como:
- Navegação privada/anônima
- VPNs
- Navegador Tor

Nosso objetivo é entender melhor essas vulnerabilidades para desenvolver contramedidas eficazes.

## 🚀 Começando

### Pré-requisitos

- Python 3.6 ou superior
- Navegadores web (Chrome, Firefox, Safari, etc.)

### ⚙️ Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/bigger-fish.git
   cd bigger-fish
   ```

2. **Instale as dependências:**
   ```bash
pip install -r requirements.txt
```

3. **Configure os drivers dos navegadores:**

   | Navegador | Instruções |
   |-----------|------------|
   | Chrome | Baixe [aqui](https://googlechromelabs.github.io/chrome-for-testing/) e adicione o `chromedriver` ao seu PATH |
   | Firefox | Baixe [aqui](https://github.com/mozilla/geckodriver/releases) e adicione o `geckodriver` ao seu PATH |
   | Safari | Não precisa instalar! O `safaridriver` já está integrado ao macOS |
   | Tor Browser | Instale o [tor-browser-selenium](https://github.com/webfp/tor-browser-selenium) |
   | Links | No macOS: `brew install links` |

## 🧪 Experimentos

### 1️⃣ Experimento Básico: Identificando Sites

Este experimento coleta "impressões digitais" de sites populares e treina um modelo para identificá-los:

```bash
# Coleta dados de 4 sites populares (40 amostras de cada, 5 segundos por amostra)
python record_data.py --num_runs 40 --trace_length 5 --sites_list alexa4 --out_directory meu-experimento
```

O script:
1. Abre cada site em um navegador
2. Mede o comportamento da CPU durante o carregamento
3. Salva esses "traços" para análise

### 2️⃣ Verificando a Precisão

Após coletar os dados, verifique quão bem o modelo consegue identificar os sites:

```bash
python scripts/check_results.py --data_file meu-experimento
```

Você verá resultados como:
```
Número de traços: 160
precisão top1: 87.3% (+/- 6.8%)  # Acerta o site exato em 87% das vezes!
precisão top5: 100.0% (+/- 0.0%) # O site correto está entre os 5 mais prováveis em 100% das vezes
```

### 🛡️ Testando Contramedidas

Podemos testar diferentes proteções contra esses ataques:

#### Contramedida de Cache
```bash
python record_data.py --num_runs 40 --trace_length 5 --sites_list alexa4 --enable_cache_countermeasure True
```
Esta contramedida tenta confundir o atacante acessando a memória cache de forma aleatória.

#### Isolamento de CPU
```bash
python record_data.py --num_runs 40 --trace_length 5 --sites_list alexa4 --attacker_type counter
```
Este experimento isola o processo atacante em um núcleo de CPU separado.

#### Jitter de Temporizador
```bash
python record_data.py --num_runs 40 --trace_length 5 --sites_list alexa4 --timer_resolution 0.001 --enable_timer_jitter True
```
Esta contramedida adiciona variações aleatórias às medições de tempo.

## 📊 Análise Avançada

Para experimentos maiores, recomendamos usar nosso modelo LSTM mais avançado:

- **Notebook Colab**: [Abrir no Google Colab](https://colab.research.google.com/drive/1GRQwuxlfoCPaiM7BiP9giHS2sMppvYHH?usp=sharing)
- Este modelo atinge precisão ainda maior ao analisar a sequência temporal dos dados

## ❓ Perguntas Frequentes

### Como funciona o ataque na prática?

1. O atacante executa um script JavaScript em segundo plano (ou outro código)
2. Este script mede o desempenho da CPU enquanto o usuário navega
3. Os dados coletados são processados por um modelo de aprendizado de máquina
4. O modelo identifica quais sites foram visitados com alta precisão

### Isso funciona em todos os navegadores?

Sim! Testamos em Chrome, Firefox, Safari e até no Tor Browser. As contramedidas atuais dos navegadores não são suficientes para impedir completamente estes ataques.

### Como posso me proteger?

- Use extensões que limitem o acesso a temporizadores de alta precisão
- Considere usar sistemas operacionais que isolem processos
- Esteja ciente que mesmo com proteções, algum vazamento de informação ainda pode ocorrer

## 📚 Citação

Se usar este trabalho em sua pesquisa, por favor cite:

```bibtex
@inproceedings{cook2022biggerfish,
    author = {Cook, Jack and Drean, Jules and Behrens, Jonathan and Yan, Mengjia},
    title = {There's Always a Bigger Fish: A Clarifying Analysis of a Machine-Learning-Assisted Side-Channel Attack},
    year = {2022},
    publisher = {Association for Computing Machinery},
    url = {https://doi.org/10.1145/3470496.3527416},
    doi = {10.1145/3470496.3527416},
    booktitle = {Proceedings of the 49th Annual International Symposium on Computer Architecture},
    pages = {204–217}
}
```

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE.md) - veja o arquivo para detalhes.

---

<div align="center">
  <p>Desenvolvido para fins educacionais e de pesquisa em segurança.</p>
  <p>⚠️ Use este código apenas em ambientes controlados e com permissão adequada. ⚠️</p>
</div>
