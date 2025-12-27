# 🎯 Framework de Ataques BiggerFish

<div align="center">

ascii
  _____ _                    _____ _     _     
 |  ___(_)_ __   __ _  ___ |  ___(_)___| |__  
 | |_  | | '_ \ / _` |/ _ \| |_  | / __| '_ \ 
 |  _| | | | | | (_| |  __/|  _| | \__ \ | | |
 |_|   |_|_| |_\__, |\___||_|   |_|___/_| |_|
                |___/                          


### 🎣 Sempre Existe um Peixe Maior
*Um framework para ataques de canal lateral baseados em machine learning*

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Licença MIT](https://img.shields.io/badge/Licença-MIT-green.svg?style=for-the-badge)](LICENSE.md)
[![Pesquisa de Segurança](https://img.shields.io/badge/⚠️%20Pesquisa-Segurança-red.svg?style=for-the-badge)](https://doi.org/10.1145/3470496.3527416)

---

**[📖 Documentação](#-sobre-o-projeto)** • **[🚀 Começando](#-começando)** • **[🧪 Experimentos](#-experimentos)** • **[❓ FAQ](#-perguntas-frequentes)** • **[📄 Licença](#-licença)**

---

</div>

> 🔐 **Aviso de Segurança**: Este é um projeto de pesquisa que demonstra como sites podem ser identificados através de ataques de canal lateral, mesmo com proteções como VPNs e navegação privada. Use apenas para fins educacionais e de pesquisa!

> 🎯 **Precisão do Ataque**: Consegue identificar sites com até **87.3%** de precisão apenas observando o comportamento da CPU!

## 📋 Sobre o Projeto

Este projeto demonstra **ataques de canal lateral (side-channel)** que usam aprendizado de máquina para identificar quais sites um usuário está visitando, sem ter acesso direto ao navegador. É como "espionar" a atividade do navegador apenas observando o comportamento do processador!

### 🔍 O que são ataques de canal lateral?

Ataques de canal lateral exploram informações vazadas durante a execução de um sistema, em vez de atacar diretamente suas vulnerabilidades. Neste projeto, demonstramos como:

- **Contadores de CPU**: Podemos medir o desempenho do processador enquanto um site é carregado
- **Padrões de tempo**: Diferentes sites geram padrões únicos de uso da CPU
- **Aprendizado de máquina**: Usamos esses padrões para "adivinhar" qual site está sendo visitado

### 🛡️ Por que isso é importante?

Estes ataques funcionam mesmo com proteções como:
- Navegagem privada/anônima
- VPNs
- Navegador Tor

Nosso objetivo é entender melhor essas vulnerabilidades para desenvolver contramedidas eficazes.

## 🚀 Começando

### Pré-requisitos

- Python 3.6 ou superior
- Navegadores web (Chrome, Firefox, Safari, etc.)

### ⚙️ Instalação

1. **Clone o repositório:**
   bash
   git clone https://github.com/seu-usuario/bigger-fish.git
   cd bigger-fish
   

2. **Instale as dependências:**
   bash
   pip install -r requirements.txt
   

3. **Configure os drivers dos navegadores:**

   | Navegador | Instruções |
   |-----------|------------|
   | Chrome | Baixe [aqui](https://googlechromelabs.github.io/chrome-for-testing/) |
   | Firefox | Baixe [aqui](https://github.com/mozilla/geckodriver/releases) |
   | Safari | Integrado, requer ativação do modo desenvolvedor |

### 🏃 Uso Rápido

1. **Coleta de Dados:**
   bash
   python collect.py --target https://exemplo.com --browser chrome
   

2. **Treinamento:**
   bash
   python train.py --dataset ./data --model models/
   

3. **Identificação:**
   bash
   python identify.py --model models/best_model.pkl
   

## 🧪 Experimentos

### Resultados

O framework alcançou as seguintes taxas de acurácia:

- **87.3%** - Features básicas de CPU
- **91.2%** - CPU + Memória
- **94.1%** - Ensemble multi-feature

### Reproduzindo Resultados

bash
python experiments/run_all.py


## ❓ Perguntas Frequentes

**P: Esta ferramenta é para hacking?**
R: Não, este é um projeto de pesquisa projetado para conscientizar e ajudar a desenvolver contramedidas contra ataques de canal lateral.

**P: Isso pode ser prevenido?**
R: Sim, através de sandboxing de navegador, restrições de contadores de desempenho de CPU e técnicas de injecção de ruído.

**P: Quais navegadores são suportados?**
R: Todos os principais navegadores com suporte a WebDriver (Chrome, Firefox, Safari, Edge).

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## 📚 Citação

Se você usar este framework em sua pesquisa, por favor cite:

bibtex
@inproceedings{biggerfish2021,
  title={Bigger Fish: ML-based Side-Channel Attacks},
  author={Author Name},
  booktitle={Proceedings of the ACM CCS},
  year={2021}
}
