# Pricer d'options & Delta Hedging

Projet de finance quantitative réalisé en Python dans le cadre d'un parcours de Master en ingénierie financière. Le dépôt regroupe des méthodes de valorisation d'options, de calcul des sensibilités, d'extraction de volatilité implicite et de couverture dynamique.

## 1. Objectifs

Le projet vise à relier les modèles mathématiques de la finance aux méthodes numériques et à l'analyse du risque :

- valoriser des options européennes avec Black-Scholes et Monte-Carlo ;
- réduire la variance d'un estimateur Monte-Carlo par variables antithétiques ;
- étudier une option asiatique arithmétique ;
- calculer et valider les Grecques ;
- retrouver la volatilité implicite par Newton-Raphson sécurisé ;
- analyser une chaîne d'options réelle AAPL ;
- simuler une couverture Delta-Neutre et mesurer l'effet de la fréquence de rebalancement et des coûts de transaction.

## 2. Architecture

```text
options-pricer-delta-hedging/
├── README.md
├── requirements.txt
├── src/
│   ├── pricing.py
│   ├── greeks.py
│   ├── volatility.py
│   └── hedging.py
├── tests/
│   ├── test_pricing.py
│   ├── test_greeks.py
│   ├── test_volatility.py
│   └── test_hedging.py
├── figures/
└── notebooks/
    └── analysis.ipynb
```

Le dossier `src/` contient les moteurs de calcul réutilisables. Le notebook est consacré aux expériences numériques, aux graphiques et à leur interprétation financière.

## 3. Modules quantitatifs

### 3.1 Pricing

- Prix des Calls et Puts européens par Black-Scholes, sans dividendes.
- Monte-Carlo standard avec intervalle de confiance à 95 %.
- Monte-Carlo à variables antithétiques.
- Valorisation Monte-Carlo d'un Call asiatique à moyenne arithmétique discrétisée.

La convergence des estimateurs est comparée au prix analytique de Black-Scholes. La réduction de variance est étudiée à nombre de trajectoires comparable.

### 3.2 Grecques

Calcul analytique de :

- Delta : sensibilité au prix du sous-jacent ;
- Gamma : sensibilité du Delta au sous-jacent ;
- Vega : sensibilité à la volatilité ;
- Theta : décroissance temporelle ;
- Rho : sensibilité au taux sans risque.

Les formules sont confrontées à des approximations par différences finies. Convention : Vega et Rho sont les dérivées par rapport à une variation de 1,00 des entrées décimales ; Theta est annualisé et défini par `-dV/dT`.

### 3.3 Volatilité implicite

La volatilité implicite est obtenue en inversant le prix Black-Scholes. Newton-Raphson est la méthode principale ; une dichotomie de sauvegarde est utilisée lorsque le pas de Newton n'est pas admissible ou que Vega est trop faible.

Le notebook vérifie la récupération de volatilités connues sur Calls et Puts, puis applique le solveur aux prix mid d'une chaîne d'options AAPL récupérée avec `yfinance`. La volatilité implicite du modèle est comparée à celle publiée par Yahoo Finance.

### 3.4 Delta Hedging

Le moteur simule une position courte sur un Call européen et sa couverture par le sous-jacent et un compte espèces rémunéré au taux sans risque.

Le notebook compare :
- rebalancement quotidien ;
- rebalancement hebdomadaire (tous les 5 pas) ;
- rebalancement mensuel (tous les 21 pas) ;
- coûts de transaction de 0, 5 et 10 points de base.

Une première comparaison utilise une trajectoire commune. Une étude complémentaire répète les simulations sur plusieurs trajectoires GBM afin d'étudier la distribution du P&L terminal, son écart-type et son RMSE.

**Périmètre actuel :** l'étude de couverture est une simulation sous GBM à taux et volatilité constants, sous la mesure risque-neutre. Elle ne constitue pas un backtest historique du S&P 500 ou du CAC 40. Les données réelles sont actuellement utilisées pour l'étude de la chaîne d'options AAPL.

## 4. Hypothèses et limites

Les résultats reposent notamment sur les hypothèses suivantes :

- options européennes ;
- modèle Black-Scholes sans dividendes pour les fonctions de pricing et de volatilité implicite ;
- taux sans risque et volatilité constants dans les simulations de couverture ;
- dynamique GBM continue échantillonnée à dates discrètes ;
- coûts de transaction proportionnels au notionnel échangé ;
- absence de sauts, de contraintes de liquidité, de bid-ask sur la couverture et de financement différencié.

Les résultats doivent donc être interprétés comme une étude pédagogique et quantitative, et non comme une recommandation d'investissement.

## 5. Figures générées

Le notebook enregistre les figures dans `figures/` :

- `convergence_monte_carlo.png` — convergence des estimateurs ;
- `delta_profile.png`, `gamma_profile.png`, `vega_profile.png`, `theta_profile.png`, `theta_maturity.png` — profils des sensibilités ;
- `volatility_smile.png`, `volatility_skew.png` — smile et skew synthétiques ;
- `aapl_calls_comparison.png`, `aapl_puts_comparison.png` — comparaison des volatilités implicites AAPL ;
- `gbm_simulation.png` — trajectoire GBM ;
- `delta_hedging_frequency.png` — P&L selon la fréquence ;
- `delta_hedging_transaction_costs.png` — effet des coûts ;
- `delta_hedging_pnl_distribution.png` — distribution du P&L terminal sur plusieurs trajectoires.

Les figures sont générées lors de l'exécution du notebook ; elles ne sont pas nécessairement présentes dans un clone avant cette exécution.

## 6. Installation

Cloner le dépôt :

```bash
git clone https://github.com/mamethiernot099-wq/options-pricer-delta-hedging.git
cd options-pricer-delta-hedging
```

Créer et activer un environnement virtuel (Windows PowerShell) :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## 7. Exécution

Depuis la racine du dépôt :

```bash
jupyter notebook notebooks/analysis.ipynb
```

Dans VS Code, ouvrir le dossier racine du dépôt, sélectionner l'interpréteur `.venv`, puis exécuter les cellules dans l'ordre avec **Run All**. La première cellule configure le chemin du projet et crée le dossier `figures/` si nécessaire.

La partie AAPL nécessite une connexion Internet et l'accès aux données Yahoo Finance. Les expirations disponibles sont sélectionnées dynamiquement parmi les dates futures renvoyées par le fournisseur.

## 8. Tests

Lancer l'ensemble des tests depuis la racine :

```bash
python -m unittest discover -s tests -v
```

Les 42 tests des quatre modules ont été exécutés avec succès dans l'environnement de développement local au cours de la validation du projet.

## 9. Pistes d'extension

- backtest de Delta Hedging sur données historiques S&P 500 ou CAC 40 ;
- calibration de la volatilité implicite et prise en compte des dividendes ;
- décomposition plus détaillée du P&L par effets Delta, Gamma, Vega et Theta ;
- modélisation de coûts de transaction et de contraintes de liquidité plus réalistes.

---

**Auteur :** Mame Thierno Thiam  
**Domaine :** Finance quantitative, mathématiques appliquées et gestion des risques
