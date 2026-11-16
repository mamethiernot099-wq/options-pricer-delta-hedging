import pandas as pd
from src.pricing import black_scholes_call
from scipy.stats import norm
import math
import numpy as np


def simulate_gbm_path(
    S0,
    r,
    sigma,
    T,
    n_steps=252,
    seed=None
):
    """
    Simulate a stock price path using
    Geometric Brownian Motion.
    """

    dt = T / n_steps

    rng = np.random.default_rng(seed)

    Z = rng.standard_normal(n_steps)

    times = np.linspace(0, T, n_steps + 1)

    prices = np.zeros(n_steps + 1)

    prices[0] = S0

    for i in range(n_steps):

        prices[i + 1] = prices[i] * np.exp(
            (r - 0.5 * sigma**2) * dt
            + sigma * np.sqrt(dt) * Z[i]
        )

    return times, prices

def calculate_call_delta(S, K, tau, r, sigma):
    """
    Calculate the Delta of a European Call
    using the Black-Scholes model.
    """

    # Vérification des paramètres
    if S <= 0 or K <= 0:
        raise ValueError("S et K doivent être positifs.")

    if sigma <= 0:
        raise ValueError("La volatilité doit être positive.")

    if tau < 0:
        raise ValueError("La maturité ne peut pas être négative.")

    # À l'échéance
    if tau == 0:
        if S > K:
            return 1.0
        elif S < K:
            return 0.0
        else:
            return 0.5

    # Calcul de d1
    d1 = (
        math.log(S / K)
        + (r + 0.5 * sigma**2) * tau
    ) / (sigma * math.sqrt(tau))

    # Delta du Call
    delta = norm.cdf(d1)

    return float(delta)



def delta_hedging_simulation(
    S0,
    K,
    T,
    r,
    sigma,
    n_steps=252,
    seed=None
):
    """
    Simulate a daily delta-hedging strategy
    for a short European Call position.

    Returns a DataFrame containing:
    - Stock price
    - Call price
    - Call Delta
    - Shares held
    - Cash account
    - Portfolio value
    """

    # 1. Simuler le cours de l'action
    times, prices = simulate_gbm_path(
        S0, r, sigma, T, n_steps, seed
    )

    dt = T / n_steps

    # 2. Prix initial du Call
    call_price = black_scholes_call(
        S0, K, T, r, sigma
    )

    # 3. Delta initial
    delta = calculate_call_delta(
        S0, K, T, r, sigma
    )

    # 4. Position initiale
    shares = delta

    # Trésorerie initiale après vente du Call
    cash = call_price - shares * S0

    results = []

    # Première observation
    results.append({
        "time": 0.0,
        "stock_price": S0,
        "call_price": call_price,
        "call_delta": delta,
        "shares_held": shares,
        "cash_account": cash,
        "portfolio_value": 0.0
    })

    # 5. Rééquilibrage quotidien
    for i in range(1, n_steps + 1):

        S = prices[i]
        tau = T - times[i]

        # Accumulation des intérêts
        cash *= math.exp(r * dt)

        if i < n_steps:

            # Nouveau Delta
            new_delta = calculate_call_delta(
                S, K, tau, r, sigma
            )

            # Variation du nombre d'actions
            delta_shares = new_delta - shares

            # Achat ou vente des actions
            cash -= delta_shares * S

            # Mise à jour de la position
            shares = new_delta

            # Nouvelle valeur du Call
            call_price = black_scholes_call(
                S, K, tau, r, sigma
            )

            current_delta = new_delta

        else:

            # À l'échéance : paiement du Call
            call_price = max(S - K, 0)

            # Plus aucun rééquilibrage
            current_delta = np.nan

        # Valeur du portefeuille
        portfolio_value = (
            cash + shares * S - call_price
        )

        results.append({
            "time": times[i],
            "stock_price": S,
            "call_price": call_price,
            "call_delta": current_delta,
            "shares_held": shares,
            "cash_account": cash,
            "portfolio_value": portfolio_value
        })

    return pd.DataFrame(results)
