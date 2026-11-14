
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
