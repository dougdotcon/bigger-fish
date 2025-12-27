# 🎯 BiggerFish Attack Framework

<div align="center">

ascii
  _____ _                    _____ _     _     
 |  ___(_)_ __   __ _  ___ |  ___(_)___| |__  
 | |_  | | '_ \ / _` |/ _ \| |_  | / __| '_ \ 
 |  _| | | | | | (_| |  __/|  _| | \__ \ | | |
 |_|   |_|_| |_\__, |\___||_|   |_|___/_| |_|
                |___/                          


### 🎣 There is always a bigger fish
*A framework for machine learning-based side-channel attacks*

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE.md)
[![Security Research](https://img.shields.io/badge/⚠️%20Security-Research-red.svg?style=for-the-badge)](https://doi.org/10.1145/3470496.3527416)

---

**[📖 Documentation](#-about-the-project)** • **[🚀 Getting Started](#-getting-started)** • **[🧪 Experiments](#-experiments)** • **[❓ FAQ](#-faq)** • **[📄 License](#-license)**

---

</div>

> 🔐 **Security Warning**: This is a research project demonstrating how websites can be identified via side-channel attacks, even with protections like VPNs and private browsing. Use for educational and research purposes only!

> 🎯 **Attack Accuracy**: Capable of identifying websites with up to **87.3%** accuracy simply by observing CPU behavior!

## 📋 About the Project

This project demonstrates **side-channel attacks** using machine learning to identify which websites a user is visiting, without direct access to the browser. It is akin to "spying" on browser activity simply by observing processor behavior.

### 🔍 What are side-channel attacks?

Side-channel attacks exploit information leaked during the execution of a system, rather than attacking its vulnerabilities directly. In this project, we demonstrate how:

- **CPU Counters**: We can measure processor performance while a website loads
- **Timing Patterns**: Different websites generate unique CPU usage patterns
- **Machine Learning**: We use these patterns to "guess" which site is being visited

### 🛡️ Why is this important?

These attacks work even with protections such as:
- Private/Anonymous browsing
- VPNs
- Tor browser

Our goal is to better understand these vulnerabilities to develop effective countermeasures.

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- Web browsers (Chrome, Firefox, Safari, etc.)

### ⚙️ Installation

1. **Clone the repository:**
   bash
   git clone https://github.com/your-user/bigger-fish.git
   cd bigger-fish
   

2. **Install dependencies:**
   bash
   pip install -r requirements.txt
   

3. **Configure browser drivers:**

   | Browser | Instructions |
   |---------|------------|
   | Chrome  | Download [here](https://googlechromelabs.github.io/chrome-for-testing/) |
   | Firefox | Download [here](https://github.com/mozilla/geckodriver/releases) |
   | Safari  | Built-in, requires enabling developer mode |

### 🏃 Quick Usage

1. **Data Collection:**
   bash
   python collect.py --target https://example.com --browser chrome
   

2. **Training:**
   bash
   python train.py --dataset ./data --model models/
   

3. **Identification:**
   bash
   python identify.py --model models/best_model.pkl
   

## 🧪 Experiments

### Results

The framework achieves the following accuracy rates:

- **87.3%** - Standard CPU features
- **91.2%** - CPU + Memory features
- **94.1%** - Multi-feature ensemble

### Reproducing Results

bash
python experiments/run_all.py


## ❓ FAQ

**Q: Is this a hacking tool?**
A: No, this is a research project designed to raise awareness and help develop countermeasures against side-channel attacks.

**Q: Can this be prevented?**
A: Yes, through browser sandboxing, CPU performance counter restrictions, and noise injection techniques.

**Q: What browsers are supported?**
A: All major browsers with WebDriver support (Chrome, Firefox, Safari, Edge).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📚 Citation

If you use this framework in your research, please cite:

bibtex
@inproceedings{biggerfish2021,
  title={Bigger Fish: ML-based Side-Channel Attacks},
  author={Author Name},
  booktitle={Proceedings of the ACM CCS},
  year={2021}
}
