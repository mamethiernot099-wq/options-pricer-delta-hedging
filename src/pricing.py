import numpy as np
import math
from scipy.stats import norm


def _validate_inputs(S0, K, T, r, sigma):
    """
    Vérifie la validité des paramètres du modèle Black-Scholes.
    """

    parameters = [S0, K, T, r, sigma]

    if not all(math.isfinite(x) for x in parameters):
        raise ValueError("Tous les paramètres doivent être finis.")

    if S0 <= 0:
        raise ValueError("Le prix initial S0 doit être positif.")

    if K <= 0:
        raise ValueError("Le strike K doit être positif.")

    if T <= 0:
        raise ValueError("La maturité T doit être strictement positive.")

    if sigma <= 0:
        raise ValueError("La volatilité sigma doit être strictement positive.")


def _calculate_d1_d2(S0, K, T, r, sigma):
    """
    Calcule les paramètres d1 et d2 de Black-Scholes.
    """

    _validate_inputs(S0, K, T, r, sigma)

    d1 = (
        math.log(S0 / K) + (r + 0.5 * sigma**2) * T
    ) / (sigma * math.sqrt(T))

    d2 = d1 - sigma * math.sqrt(T)

    return d1, d2


def black_scholes_call(S0, K, T, r, sigma):
    """
    Calcule le prix d'un Call européen sans dividendes.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    call_price = (
        S0 * norm.cdf(d1)
        - K * math.exp(-r * T) * norm.cdf(d2)
    )

    return float(call_price)


def black_scholes_put(S0, K, T, r, sigma):
    """
    Calcule le prix d'un Put européen sans dividendes.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    put_price = (
        K * math.exp(-r * T) * norm.cdf(-d2)
        - S0 * norm.cdf(-d1)
    )

    return float(put_price)

def monte_carlo_call(S0, K, T, r, sigma,
                     n_simulations=100_000, seed=None):
    """
    Estime le prix d'un Call européen par Monte-Carlo.

    Paramètres
    ----------
    S0 : float
        Prix initial du sous-jacent.
    K : float
        Prix d'exercice.
    T : float
        Maturité en années.
    r : float
        Taux sans risque.
    sigma : float
        Volatilité annuelle.
    n_simulations : int
        Nombre de simulations.
    seed : int ou None
        Graine aléatoire pour reproductibilité.

    Retour
    ------
    dict
        Prix estimé, erreur standard et intervalle
        de confiance à 95 %.
    """

    _validate_inputs(S0, K, T, r, sigma)

    if not isinstance(n_simulations, int) or isinstance(n_simulations, bool) or n_simulations < 2:
        raise ValueError("Il faut au moins 2 simulations.")

    # 1. Génération des variables normales
    rng = np.random.default_rng(seed)

    Z = rng.standard_normal(n_simulations)

    # 2. Simulation des prix à maturité
    ST = S0 * np.exp(
        (r - 0.5 * sigma**2) * T
        + sigma * np.sqrt(T) * Z
    )

    # 3. Calcul des payoffs du Call
    payoffs = np.maximum(ST - K, 0)

    # 4. Actualisation des payoffs
    discounted_payoffs = np.exp(-r * T) * payoffs

    # 5. Estimation du prix
    price = np.mean(discounted_payoffs)

    # 6. Erreur standard
    standard_error = (
        np.std(discounted_payoffs, ddof=1)
        / np.sqrt(n_simulations)
    )

    # 7. Intervalle de confiance à 95 %
    confidence_interval = (
        price - 1.96 * standard_error,
        price + 1.96 * standard_error
    )

    return {
        "price": float(price),
        "standard_error": float(standard_error),
        "confidence_interval": confidence_interval,
        "n_simulations": n_simulations
    }

def monte_carlo_call_antithetic(
    S0, K, T, r, sigma,
    n_pairs=50_000,
    seed=None
):
    """
    Estime le prix d'un Call européen avec
    la méthode des variables antithétiques.

    n_pairs représente le nombre de paires,
    soit 2 * n_pairs trajectoires au total.
    """

    _validate_inputs(S0, K, T, r, sigma)

    if not isinstance(n_pairs, int) or isinstance(n_pairs, bool) or n_pairs < 2:
        raise ValueError("Il faut au moins 2 paires.")

    # 1. Génération des variables normales
    rng = np.random.default_rng(seed)

    Z = rng.standard_normal(n_pairs)

    # 2. Simulation des deux prix opposés
    drift = (r - 0.5 * sigma**2) * T
    diffusion = sigma * np.sqrt(T)

    ST_plus = S0 * np.exp(drift + diffusion * Z)
    ST_minus = S0 * np.exp(drift - diffusion * Z)

    # 3. Calcul des payoffs
    payoff_plus = np.maximum(ST_plus - K, 0)
    payoff_minus = np.maximum(ST_minus - K, 0)

    # 4. Moyenne des payoffs antithétiques
    paired_payoffs = (
        payoff_plus + payoff_minus
    ) / 2

    # 5. Actualisation
    discounted_payoffs = (
        np.exp(-r * T) * paired_payoffs
    )

    # 6. Estimation du prix
    price = np.mean(discounted_payoffs)

    # 7. Erreur standard
    standard_error = (
        np.std(discounted_payoffs, ddof=1)
        / np.sqrt(n_pairs)
    )

    # 8. Intervalle de confiance à 95 %
    confidence_interval = (
        price - 1.96 * standard_error,
        price + 1.96 * standard_error
    )

    return {
        "price": float(price),
        "standard_error": float(standard_error),
        "confidence_interval": tuple(
            float(x) for x in confidence_interval
        ),
        "n_pairs": n_pairs,
        "n_simulations": 2 * n_pairs
    }

def monte_carlo_asian_call(
    S0, K, T, r, sigma,
    n_simulations=50_000,
    n_steps=252,
    seed=None
):
    """
    Price an arithmetic Asian Call using Monte Carlo.

    The arithmetic average is calculated over n_steps
    equally spaced observations, including maturity T
    and excluding the initial spot S0.
    """

    _validate_inputs(S0, K, T, r, sigma)

    if (not isinstance(n_simulations, int)
            or isinstance(n_simulations, bool)
            or n_simulations < 2):
        raise ValueError("At least 2 simulations are required.")

    if (not isinstance(n_steps, int)
            or isinstance(n_steps, bool)
            or n_steps < 1):
        raise ValueError("n_steps must be a positive integer.")

    rng = np.random.default_rng(seed)

    # Time discretization
    dt = T / n_steps

    # Risk-neutral dynamics
    drift = (r - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)

    # Initial stock prices
    ST = np.full(n_simulations, S0, dtype=float)

    # Sum of observed prices
    price_sum = np.zeros(n_simulations)

    # Simulate the trajectories
    for j in range(n_steps):

        Z = rng.standard_normal(n_simulations)

        ST *= np.exp(drift + diffusion * Z)

        price_sum += ST

    # Arithmetic average
    average_price = price_sum / n_steps

    # Asian Call payoff
    payoffs = np.maximum(average_price - K, 0)

    # Discounted payoffs
    discounted_payoffs = np.exp(-r * T) * payoffs

    # Price estimation
    price = np.mean(discounted_payoffs)

    # Standard error
    standard_error = (
        np.std(discounted_payoffs, ddof=1)
        / np.sqrt(n_simulations)
    )

    # 95% confidence interval
    confidence_interval = (
        price - 1.96 * standard_error,
        price + 1.96 * standard_error
    )

    return {
        "price": float(price),
        "standard_error": float(standard_error),
        "confidence_interval": tuple(
            float(x) for x in confidence_interval
        ),
        "n_simulations": n_simulations,
        "n_steps": n_steps
    }
