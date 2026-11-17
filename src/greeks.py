"""Black-Scholes Greeks for European options without dividends.

Conventions:
- Vega is the derivative with respect to volatility expressed as a decimal
  (a change of 1.00, i.e. 100 percentage points).
- Rho is the derivative with respect to the continuously compounded rate
  expressed as a decimal (a change of 1.00).
- Theta is annualized calendar-time decay, equal to -dV/dT.
"""

import math

from scipy.stats import norm

from src.pricing import _calculate_d1_d2


def delta_call(S0, K, T, r, sigma):
    """Return the spot sensitivity of a European Call."""
    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)
    return float(norm.cdf(d1))


def delta_put(S0, K, T, r, sigma):
    """Return the spot sensitivity of a European Put."""
    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)
    return float(norm.cdf(d1) - 1.0)


def gamma(S0, K, T, r, sigma):
    """Return the second spot derivative; identical for Call and Put."""
    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)
    value = norm.pdf(d1) / (S0 * sigma * math.sqrt(T))
    return float(value)


def vega(S0, K, T, r, sigma):
    """Return dV/dsigma for a volatility change expressed as a decimal."""
    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)
    return float(S0 * norm.pdf(d1) * math.sqrt(T))


def theta_call(S0, K, T, r, sigma):
    """Return annualized Call theta, i.e. -dV/dT."""
    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)
    value = (
        -S0 * norm.pdf(d1) * sigma / (2.0 * math.sqrt(T))
        - r * K * math.exp(-r * T) * norm.cdf(d2)
    )
    return float(value)


def theta_put(S0, K, T, r, sigma):
    """Return annualized Put theta, i.e. -dV/dT."""
    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)
    value = (
        -S0 * norm.pdf(d1) * sigma / (2.0 * math.sqrt(T))
        + r * K * math.exp(-r * T) * norm.cdf(-d2)
    )
    return float(value)


def rho_call(S0, K, T, r, sigma):
    """Return dV/dr for a continuously compounded rate change as a decimal."""
    _, d2 = _calculate_d1_d2(S0, K, T, r, sigma)
    return float(K * T * math.exp(-r * T) * norm.cdf(d2))


def rho_put(S0, K, T, r, sigma):
    """Return dV/dr for a continuously compounded rate change as a decimal."""
    _, d2 = _calculate_d1_d2(S0, K, T, r, sigma)
    return float(-K * T * math.exp(-r * T) * norm.cdf(-d2))


def calculate_greeks(S0, K, T, r, sigma, option_type="call"):
    """Return Delta, Gamma, Vega, Theta and Rho for a European option.

    The option is assumed to be European and to pay no dividends.
    Vega and Rho are per unit (1.00) change in their decimal inputs;
    Theta is annualized and follows the convention -dV/dT.
    """
    if not isinstance(option_type, str):
        raise ValueError("option_type must be 'call' or 'put'")

    option_type = option_type.strip().lower()

    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")

    if option_type == "call":
        delta = delta_call
        theta = theta_call
        rho = rho_call
    else:
        delta = delta_put
        theta = theta_put
        rho = rho_put

    return {
        "Delta": delta(S0, K, T, r, sigma),
        "Gamma": gamma(S0, K, T, r, sigma),
        "Vega": vega(S0, K, T, r, sigma),
        "Theta": theta(S0, K, T, r, sigma),
        "Rho": rho(S0, K, T, r, sigma),
    }
