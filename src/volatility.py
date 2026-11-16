"""Implied volatility solvers for European Black-Scholes options.

Newton-Raphson is used as the primary method. A bisection fallback keeps
iterations inside a valid volatility bracket when a Newton step is unsafe.
The model assumes European options on a non-dividend-paying underlying.
"""

import math

from src.pricing import black_scholes_call, black_scholes_put
from src.greeks import vega


def _implied_volatility(
    market_price,
    S0,
    K,
    T,
    r,
    option_type,
    initial_sigma=0.20,
    tolerance=1e-8,
    max_iterations=100,
):
    """Solve for volatility using safeguarded Newton-Raphson."""
    numeric_parameters = {
        "market_price": market_price,
        "initial_sigma": initial_sigma,
        "tolerance": tolerance,
    }
    for name, value in numeric_parameters.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a real number.")
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} must be finite.")

    if initial_sigma <= 0:
        raise ValueError("initial_sigma must be strictly positive.")
    if tolerance <= 0:
        raise ValueError("tolerance must be strictly positive.")
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int):
        raise ValueError("max_iterations must be a positive integer.")
    if max_iterations < 1:
        raise ValueError("max_iterations must be a positive integer.")

    # Reuse the pricing module's validation of S0, K, T, r and sigma.
    pricer = black_scholes_call if option_type == "call" else black_scholes_put
    pricer(S0, K, T, r, initial_sigma)

    discounted_strike = K * math.exp(-r * T)
    if option_type == "call":
        lower_bound = max(S0 - discounted_strike, 0.0)
        upper_bound = S0
    else:
        lower_bound = max(discounted_strike - S0, 0.0)
        upper_bound = discounted_strike

    if not lower_bound < market_price < upper_bound:
        raise ValueError(
            f"market_price must be strictly between the no-arbitrage "
            f"bounds ({lower_bound:.12g}, {upper_bound:.12g})."
        )

    # Establish a bracket [low, high] containing the implied volatility.
    low = 1e-10
    high = max(float(initial_sigma), 0.5)
    price_high = pricer(S0, K, T, r, high)

    while price_high < market_price and high < 1e3:
        high *= 2.0
        price_high = pricer(S0, K, T, r, high)

    if price_high < market_price:
        raise RuntimeError("Could not bracket the implied volatility.")

    sigma = min(max(float(initial_sigma), low), high)

    for _ in range(max_iterations):
        theoretical_price = pricer(S0, K, T, r, sigma)
        error = theoretical_price - market_price

        if abs(error) <= tolerance:
            return float(sigma)

        # Update the bracket using monotonicity of Black-Scholes price in sigma.
        if error < 0:
            low = sigma
        else:
            high = sigma

        vega_value = vega(S0, K, T, r, sigma)

        # Newton step when Vega is sufficiently large and the candidate
        # remains strictly inside the bracket; otherwise use bisection.
        if math.isfinite(vega_value) and vega_value > 1e-12:
            candidate = sigma - error / vega_value
        else:
            candidate = math.nan

        if not math.isfinite(candidate) or not low < candidate < high:
            candidate = 0.5 * (low + high)

        sigma = candidate

    # Check once more at the last iterate before reporting non-convergence.
    if abs(pricer(S0, K, T, r, sigma) - market_price) <= tolerance:
        return float(sigma)

    raise RuntimeError(
        f"Implied volatility did not converge in {max_iterations} iterations."
    )


def implied_volatility_call(
    market_price,
    S0,
    K,
    T,
    r,
    initial_sigma=0.20,
    tolerance=1e-8,
    max_iterations=100,
):
    """Return the implied volatility of a European Call."""
    return _implied_volatility(
        market_price, S0, K, T, r, "call",
        initial_sigma, tolerance, max_iterations,
    )


def implied_volatility_put(
    market_price,
    S0,
    K,
    T,
    r,
    initial_sigma=0.20,
    tolerance=1e-8,
    max_iterations=100,
):
    """Return the implied volatility of a European Put."""
    return _implied_volatility(
        market_price, S0, K, T, r, "put",
        initial_sigma, tolerance, max_iterations,
    )
