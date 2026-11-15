
import math
from scipy.stats import norm

from src.pricing import _calculate_d1_d2


def delta_call(S0, K, T, r, sigma):
    """
    Calculate the Delta of a European Call.
    """

    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)

    return float(norm.cdf(d1))


def delta_put(S0, K, T, r, sigma):
    """
    Calculate the Delta of a European Put.
    """

    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)

    return float(norm.cdf(d1) - 1)

def gamma(S0, K, T, r, sigma):
    """
    Calculate the Gamma of a European Call or Put.
    Gamma is identical for Calls and Puts.
    """

    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)

    gamma_value = (
        norm.pdf(d1)
        / (S0 * sigma * math.sqrt(T))
    )

    return float(gamma_value)

def vega(S0, K, T, r, sigma):
    """
    Calculate the Vega of a European Call or Put.

    The result is expressed for a volatility change
    of 1.00 (100 percentage points).
    """

    d1, _ = _calculate_d1_d2(S0, K, T, r, sigma)

    vega_value = (
        S0 * norm.pdf(d1) * math.sqrt(T)
    )

    return float(vega_value)

def theta_call(S0, K, T, r, sigma):
    """
    Calculate the annualized Theta of a European Call.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    theta_value = (
        -S0 * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * norm.cdf(d2)
    )

    return float(theta_value)


def theta_put(S0, K, T, r, sigma):
    """
    Calculate the annualized Theta of a European Put.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    theta_value = (
        -S0 * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
        + r * K * math.exp(-r * T) * norm.cdf(-d2)
    )

    return float(theta_value)

def rho_call(S0, K, T, r, sigma):
    """
    Calculate the Rho of a European Call.
    Expressed for a rate change of 1.00.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    rho_value = (
        K * T * math.exp(-r * T) * norm.cdf(d2)
    )

    return float(rho_value)


def rho_put(S0, K, T, r, sigma):
    """
    Calculate the Rho of a European Put.
    Expressed for a rate change of 1.00.
    """

    d1, d2 = _calculate_d1_d2(S0, K, T, r, sigma)

    rho_value = (
        -K * T * math.exp(-r * T) * norm.cdf(-d2)
    )

    return float(rho_value)

def calculate_greeks(S0, K, T, r, sigma, option_type="call"):
    """
    Calculate all five Greeks of a European option.

    Parameters
    ----------
    option_type : str
        "call" or "put"

    Returns
    -------
    dict
        Delta, Gamma, Vega, Theta and Rho.
        Vega and Rho are expressed for a change of 1.00.
        Theta is annualized.
    """

    option_type = option_type.lower()

    if option_type == "call":

        return {
            "Delta": delta_call(S0, K, T, r, sigma),
            "Gamma": gamma(S0, K, T, r, sigma),
            "Vega": vega(S0, K, T, r, sigma),
            "Theta": theta_call(S0, K, T, r, sigma),
            "Rho": rho_call(S0, K, T, r, sigma)
        }

    elif option_type == "put":

        return {
            "Delta": delta_put(S0, K, T, r, sigma),
            "Gamma": gamma(S0, K, T, r, sigma),
            "Vega": vega(S0, K, T, r, sigma),
            "Theta": theta_put(S0, K, T, r, sigma),
            "Rho": rho_put(S0, K, T, r, sigma)
        }

    else:
        raise ValueError("option_type must be 'call' or 'put'")
