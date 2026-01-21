# Projet JVX

# 🧬 Sujet 41 : Stratégies de Trading par Algorithmes Génétiques

> **Projet IA & Finance - ECE Paris (2026)**
> **Groupe JVX** : Jean-François, Valentin, Xavier

## 📋 Description du Projet

L'optimisation de stratégies de trading algorithmique est un défi majeur en finance quantitative. Elle nécessite l'exploration d'un **espace combinatoire immense** composé de multiples indicateurs techniques, de seuils et de règles de décision. Les méthodes d'optimisation classiques peinent souvent à trouver des solutions robustes sans tomber dans le piège du surapprentissage (*overfitting*).

Ce projet explore l'utilisation des **Algorithmes Génétiques (AG)** pour automatiser la découverte et l'optimisation de ces stratégies. En mimant la sélection naturelle, nous faisons évoluer une population de stratégies de trading pour maximiser des objectifs de performance tout en contrôlant le risque.

### Objectifs Principaux

* **Évolution :** Générer automatiquement des stratégies combinant indicateurs (RSI, SMA, MACD...) et règles logiques.
* **Optimisation Multi-objectifs :** Maximiser le rendement tout en minimisant le risque (Ratio de Sharpe, Max Drawdown).
* **Robustesse :** Valider les stratégies via des techniques de *Walk-Forward Analysis* pour garantir leur viabilité sur des données inconnues.

## 📂 Structure du Dépôt

Conformément aux consignes, l'ensemble du travail est organisé dans ce répertoire dédié :

```text
/groupe-JVX-trading-genetique/
│
├── README.md              # Documentation principale du projet (ce fichier)
├── requirements.txt       # Liste des dépendances Python
│
├── src/                   # Code source du projet
│   ├── evolution/         # Moteur génétique (DEAP/PyGAD)
│   ├── strategies/        # Logique de trading et encodage des chromosomes
│   ├── backtest/          # Moteur de simulation (Backtrader)
│   └── data/              # Scripts de récupération/traitement des données
│
├── docs/                  # Documentation technique détaillée
│   ├── architecture.md    # Architecture logicielle
│   └── rapport_analyse.pdf # Rapport d'analyse des résultats
│
├── slides/                # Support de présentation
│   └── presentation.pdf   # Slides pour la soutenance
│
└── tests/                 # Tests unitaires et d'intégration

```

## ⚙️ Approche Méthodologique

Notre approche repose sur trois piliers techniques détaillés ci-dessous :

### 1. Encodage Génétique (Chromosomes)

Chaque stratégie est encodée sous forme d'un chromosome comprenant :

* **Gènes d'Indicateurs :** Paramètres des indicateurs (ex: Période RSI = 14, Fenêtre SMA = 50).
* **Gènes de Décision :** Opérateurs logiques et seuils (ex: Acheter si `RSI < 30`).
* **Gènes de Gestion :** Niveaux de Stop-Loss et Take-Profit.

### 2. Fonction de Fitness Multi-Objectifs

Pour éviter les stratégies trop risquées, notre fonction d'évaluation (fitness) ne se base pas uniquement sur le profit. Elle combine :


### 3. Validation Walk-Forward

Pour contrer le *curve-fitting* (surapprentissage des données passées), nous utilisons une validation fenêtrée glissante (Walk-Forward Testing) : l'algorithme optimise sur une période  et teste immédiatement sur la période  (inconnue), répétant ce processus sur l'ensemble de l'historique.

## 🛠 Technologies Utilisées

* **Langage :** Python 3.10+
* **Algorithmes Génétiques :** [DEAP](https://deap.readthedocs.io/) ou [PyGAD](https://pygad.readthedocs.io/)
* **Backtesting :** [Backtrader](https://www.backtrader.com/) (ou Zipline)
* **Analyse Technique :** [TA-Lib](https://ta-lib.org/) (Technical Analysis Library)
* **Données :** Pandas, yfinance, QuantConnect

## 🚀 Installation et Utilisation

### Prérequis

Ce projet nécessite **TA-Lib**. L'installation de cette librairie peut être complexe car elle requiert des binaires C++.

* *Windows :* Téléchargez le fichier `.whl` correspondant à votre version de Python [ici](https://github.com/cgohlke/talib-build/releases) avant de l'installer avec pip.
* *macOS :* `brew install ta-lib`
* *Linux :* `sudo apt-get install ta-lib`

### Installation

1. Clonez le dépôt (si ce n'est pas déjà fait).
2. Accédez au répertoire du groupe :
```bash
cd groupe-JVX-trading-genetique

```


3. Installez les dépendances :
```bash
pip install -r requirements.txt

```



### Exécution

Pour lancer une session d'optimisation génétique sur l'action Apple (AAPL) :

```bash
python src/main.py --ticker AAPL --pop_size 50 --generations 20

```

Pour lancer uniquement le backtest de la meilleure stratégie sauvegardée :

```bash
python src/main.py --mode backtest --strategy output/best_strategy.json

```

## 📚 Références Bibliographiques

Ce travail s'appuie sur la littérature scientifique récente :

1. *Robust Metaheuristic Optimization for Algorithmic Trading* - MDPI Mathematics (2024)
2. *Applicability of genetic algorithms for stock market prediction: A systematic survey* - ScienceDirect (2024)
3. *A genetic algorithm for multi-threshold trading strategies* - Artificial Intelligence Review (2025)
4. *Evolving Financial Trading Strategies with Vectorial Genetic Programming* - arXiv (2025)

## 🧪 Tests

Les tests unitaires vérifient la validité des chromosomes et le calcul correct des indicateurs.

```bash
# Lancer la suite de tests
pytest tests/

```

---

*Projet réalisé dans le cadre du cours "IA Exploratoire et Symbolique" de l'ECE Paris.*