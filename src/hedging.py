"""GBM simulation and discrete delta hedging for a short European Call."""

import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from src.pricing import _calculate_d1_d2, _validate_inputs, black_scholes_call


def _validate_n_steps(n_steps):
    if isinstance(n_steps, bool) or not isinstance(n_steps, int) or n_steps < 1:
        raise ValueError("n_steps must be a positive integer.")


def simulate_gbm_path(S0, r, sigma, T, n_steps=252, seed=None):
    """Simulate a risk-neutral GBM path with exact time-step transitions."""
    _validate_inputs(S0, 1.0, T, r, sigma)
    _validate_n_steps(n_steps)

    dt = T / n_steps
    rng = np.random.default_rng(seed)
    shocks = rng.standard_normal(n_steps)
    times = np.linspace(0.0, T, n_steps + 1)

    log_returns = (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * shocks
    prices = np.empty(n_steps + 1, dtype=float)
    prices[0] = S0
    prices[1:] = S0 * np.exp(np.cumsum(log_returns))

    return times, prices


def calculate_call_delta(S, K, tau, r, sigma):
    """Return Black-Scholes Call Delta, with a defined expiry convention."""
    if tau == 0:
        if not isinstance(S, (int, float)) or isinstance(S, bool) or not math.isfinite(S) or S <= 0:
            raise ValueError("S must be a finite positive number.")
        if not isinstance(K, (int, float)) or isinstance(K, bool) or not math.isfinite(K) or K <= 0:
            raise ValueError("K must be a finite positive number.")
        if S > K:
            return 1.0
        if S < K:
            return 0.0
        return 0.5

    d1, _ = _calculate_d1_d2(S, K, tau, r, sigma)
    return float(norm.cdf(d1))


def _rebalance_interval(rebalance_frequency, n_steps):
    if not isinstance(rebalance_frequency, str):
        raise ValueError("rebalance_frequency must be 'daily', 'weekly' or 'monthly'.")
    frequency = rebalance_frequency.strip().lower()
    intervals = {"daily": 1, "weekly": 5, "monthly": 21}
    if frequency not in intervals:
        raise ValueError("rebalance_frequency must be 'daily', 'weekly' or 'monthly'.")
    return intervals[frequency]


def delta_hedging_simulation(
    S0,
    K,
    T,
    r,
    sigma,
    n_steps=252,
    seed=None,
    rebalance_frequency="daily",
    transaction_cost_bps=0.0,
):
    """Simulate a short Call hedged with the underlying.

    The strategy sells one European Call, buys its initial Black-Scholes
    Delta in shares, and rebalances at the selected frequency. Cash accrues
    continuously at r. Transaction costs are charged on the absolute
    traded notional, including the initial hedge, in basis points.

    The returned portfolio_value is marked to market as cash + stock hedge
    minus the outstanding Call liability. At maturity the Call liability
    is its intrinsic value; the stock hedge is not forcibly liquidated.
    """
    _validate_inputs(S0, K, T, r, sigma)
    _validate_n_steps(n_steps)

    if isinstance(transaction_cost_bps, bool) or not isinstance(transaction_cost_bps, (int, float)):
        raise ValueError("transaction_cost_bps must be a non-negative number.")
    if not math.isfinite(float(transaction_cost_bps)) or transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be a finite non-negative number.")

    rebalance_every = _rebalance_interval(rebalance_frequency, n_steps)
    times, prices = simulate_gbm_path(S0, r, sigma, T, n_steps, seed)
    dt = T / n_steps

    call_price = black_scholes_call(S0, K, T, r, sigma)
    shares = calculate_call_delta(S0, K, T, r, sigma)

    initial_traded_notional = abs(shares * S0)
    initial_cost = initial_traded_notional * transaction_cost_bps / 10000.0
    cash = call_price - shares * S0 - initial_cost
    cumulative_cost = initial_cost

    results = [{
        "time": 0.0,
        "stock_price": S0,
        "call_price": call_price,
        "call_delta": shares,
        "shares_held": shares,
        "cash_account": cash,
        "portfolio_value": cash + shares * S0 - call_price,
        "transaction_cost": initial_cost,
        "cumulative_transaction_cost": cumulative_cost,
        "rebalanced": True,
    }]

    for i in range(1, n_steps + 1):
        S = float(prices[i])
        tau = max(T - float(times[i]), 0.0)
        cash *= math.exp(r * dt)
        transaction_cost = 0.0
        rebalanced = False

        if i < n_steps and i % rebalance_every == 0:
            new_delta = calculate_call_delta(S, K, tau, r, sigma)
            delta_shares = new_delta - shares
            traded_notional = abs(delta_shares * S)
            transaction_cost = traded_notional * transaction_cost_bps / 10000.0
            cash -= delta_shares * S + transaction_cost
            shares = new_delta
            rebalanced = True

        if i == n_steps:
            call_price = max(S - K, 0.0)
            current_delta = np.nan
        else:
            call_price = black_scholes_call(S, K, tau, r, sigma)
            current_delta = calculate_call_delta(S, K, tau, r, sigma)

        cumulative_cost += transaction_cost
        portfolio_value = cash + shares * S - call_price

        results.append({
            "time": float(times[i]),
            "stock_price": S,
            "call_price": call_price,
            "call_delta": current_delta,
            "shares_held": shares,
            "cash_account": cash,
            "portfolio_value": portfolio_value,
            "transaction_cost": transaction_cost,
            "cumulative_transaction_cost": cumulative_cost,
            "rebalanced": rebalanced,
        })

    return pd.DataFrame(results)
