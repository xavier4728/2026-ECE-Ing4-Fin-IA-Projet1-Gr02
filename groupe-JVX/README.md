Système de Trading Algorithmique avec Algorithmes Génétiques
Équipe JVX

Jean-François
Valentin
Xavier


🚀 Installation

Python 3.10 ou 3.11 (éviter 3.12+)
Windows 10/11 (optimisé pour Windows)

.\.venv\Scripts\Activate.ps1

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

###dashboard 

cd groupe-JVX
streamlit run dashboard.py


###terminal 


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



#