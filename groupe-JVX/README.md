Système de Trading Algorithmique avec Algorithmes Génétiques
Équipe JVX

Jean-François
Valentin
Xavier

📋 Vue d'ensemble
Ce projet implémente un système complet de trading algorithmique utilisant des Algorithmes Génétiques (GA) pour optimiser une stratégie quantitative basée sur des indicateurs techniques (SMA, RSI). Le système utilise Backtrader pour le backtesting et DEAP pour l'optimisation génétique.
Caractéristiques principales
✅ Optimisation Multi-Objectif : Maximise le profit tout en minimisant le drawdown
✅ Walk-Forward Analysis : Validation robuste contre l'overfitting
✅ Gestion des erreurs : Système résilient qui ne plante jamais
✅ Compatibilité Windows : Protection multiprocessing complète
✅ Code propre : Type hints, docstrings complètes, architecture modulaire
🏗️ Architecture
algo_trading_project/
├── data/                       # Données de marché cachées (CSV)
├── logs/                       # Logs d'exécution
├── src/
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration centralisée
│   ├── data_manager.py        # Téléchargement et gestion des données
│   ├── strategy_genes.py      # Stratégie Backtrader paramétrable
│   ├── backtest_runner.py     # Moteur de backtesting
│   ├── ga_core.py             # Algorithme génétique (DEAP)
│   └── walk_forward.py        # Walk-Forward Analysis
├── main.py                    # Point d'entrée CLI
├── requirements.txt           # Dépendances Python
└── README_PROJET.md          # Ce fichier
🧬 Chromosome (7 Gènes)
GèneSignificationTypePlageSMA_FSMA Rapideint[5, 50]SMA_SSMA Lenteint[50, 200]RSI_PPériode RSIint[5, 30]RSI_UPRSI Surachetéint[60, 90]RSI_LORSI Survenduint[10, 40]SLStop Loss (%)float[0.01, 0.10]TPTake Profit (%)float[0.02, 0.20]
📊 Stratégie de Trading
Conditions d'Entrée (Long uniquement)

Prix de clôture > SMA Rapide
SMA Rapide > SMA Lente
RSI < Seuil Survendu

Conditions de Sortie

RSI > Seuil Suracheté OU
Prix de clôture < SMA Lente

Gestion des Ordres

Utilise buy_bracket pour SL/TP automatiques
Stop Loss : prix × (1 - SL)
Take Profit : prix × (1 + TP)

🚀 Installation
Prérequis

Python 3.10 ou 3.11 (éviter 3.12+)
Windows 10/11 (optimisé pour Windows)

Installation des dépendances
bashpip install -r requirements.txt
Contenu de requirements.txt
backtrader==1.9.78.123
deap==1.4.1
yfinance==0.2.28
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
💻 Utilisation
Mode Test (Téléchargement des données uniquement)
python main.py --mode test
Mode Simple (Optimisation GA unique)
python main.py --mode simple
Mode Walk-Forward Analysis
python main.py --mode wfa
Mode Complet (Pipeline complet)
python main.py --mode all
Options avancées
python main.py --mode wfa --ticker SPY --generations 20 --population 100
Paramètres CLI disponibles

--mode : Mode d'exécution (test, simple, wfa, all)
--ticker : Symbole de trading (défaut: BTC-USD)
--generations : Nombre de générations GA (défaut: 10)
--population : Taille de la population GA (défaut: 50)

⚙️ Configuration
Modifiez src/config.py pour ajuster :
python# Données de marché
TICKER = "BTC-USD"  # ou "SPY" pour actions
INTERVAL = "1d"
START_DATE = "2020-01-01"
END_DATE = "2024-01-01"

# Backtesting
INITIAL_CASH = 10_000.0
COMMISSION_CRYPTO = 0.001
COMMISSION_STOCK = 0.0001

# Algorithme Génétique
GA_POPULATION = 50
GA_GENERATIONS = 10
GA_CXPB = 0.7  # Probabilité de croisement
GA_MUTPB = 0.2  # Probabilité de mutation

# Walk-Forward Analysis
WFA_TRAIN_MONTHS = 12  # Fenêtre d'entraînement
WFA_TEST_MONTHS = 3    # Fenêtre de test
WFA_STEP_MONTHS = 3    # Pas de glissement
📈 Walk-Forward Analysis
Principe

Fenêtre glissante : Entraînement sur 12 mois, test sur 3 mois
Optimisation GA sur les données d'entraînement
Validation sur les données out-of-sample (OOS)
Glissement de 3 mois et répétition

Métriques calculées

Performance OOS moyenne/médiane
Taux de victoire des fenêtres
Comparaison vs Buy & Hold
Drawdown maximum
Ratio de Sharpe

🛡️ Gestion des Erreurs
Le système est conçu pour ne jamais crasher :
python# Backtest échoué → fitness minimale
(-infinity, +infinity)

# Pas de trades → pénalité
(-100.0, 100.0)

# Erreur de division par zéro → gestion automatique
try/except avec retours sécurisés
📊 Résultats Attendus
Sortie typique d'une WFA
==================================================================
WALK-FORWARD ANALYSIS SUMMARY
==================================================================
Total Windows: 12

Aggregate Stats:
  mean_profit: 5.23%
  median_profit: 4.87%
  win_rate: 66.67%
  max_drawdown: -12.34%

Buy & Hold Benchmark:
  profit_pct: 45.67%
==================================================================
🔧 Débogage
Problèmes courants
1. Erreur de pickling (Windows)

✅ Toutes les fonctions d'évaluation sont au niveau module
✅ Protection if __name__ == "__main__"

2. Backtests vides

✅ Gestion automatique avec fitness minimale
✅ Validation des paramètres (SMA_F < SMA_S)

3. Données manquantes

✅ Cache automatique dans data/
✅ Sanitization complète (NaN, index, colonnes)

📚 Dépendances Techniques
Backtrader

Backtesting de stratégies de trading
Analyseurs intégrés (TradeAnalyzer, DrawDown, Sharpe)
Gestion d'ordres complexes (bracket orders)

DEAP (Distributed Evolutionary Algorithms in Python)

Algorithmes génétiques
Optimisation multi-objectif (NSGA-II)
Opérateurs génétiques (crossover, mutation)

Yahoo Finance (yfinance)

Téléchargement de données de marché gratuites
Support crypto, actions, indices
Données OHLCV

🎯 Phases d'Implémentation
✅ Phase 1 - Infrastructure

Configuration centralisée
Gestionnaire de données
Stratégie paramétrable
Backtest manuel

✅ Phase 2 - Moteur GA

Intégration DEAP
Fitness multi-objectif
Opérateurs génétiques
Validation sur 1 génération

✅ Phase 3 - Validation

Walk-Forward Analysis
CLI complète
Logging et rapports
Benchmark Buy & Hold

🚨 Points Critiques
⚠️ Contraintes

SMA_F doit être < SMA_S : Sinon pas de signal valide
Données suffisantes : Minimum ~100 barres pour backtest
Windows multiprocessing : Fonctions top-level uniquement

🎯 Objectifs de Fitness

Maximiser : Profit (%)
Minimiser : Drawdown (%)
Poids : (1.0, -1.0)

📝 Licence & Crédits
Projet académique développé par l'équipe JVX :

Jean-François
Valentin
Xavier

Technologies utilisées :

Backtrader - Backtesting framework
DEAP - Evolutionary algorithms
yfinance - Market data

🔮 Améliorations Futures

 Support de stratégies short
 Optimisation multi-actifs
 Interface graphique (GUI)
 Export des résultats (JSON, CSV)
 Visualisations avancées (matplotlib)
 Machine Learning (features engineering)
 Trading en temps réel (paper trading)

📞 Support
Pour toute question ou problème :

Vérifier les logs dans logs/
Consulter SPECIFICATIONS.md
Contacter l'équipe JVX


Bon trading algorithmique ! 🚀📈