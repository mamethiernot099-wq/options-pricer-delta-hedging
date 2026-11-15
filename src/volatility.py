from src.pricing import black_scholes_put
from src.pricing import black_scholes_call
from src.greeks import vega

def implied_volatility_call(
    market_price,
    S0,
    K,
    T,
    r,
    initial_sigma=0.20,
    tolerance=1e-8,
    max_iterations=100
):
    """
    Calculate the implied volatility of a European Call
    using the Newton-Raphson method.
    """

    # Initialisation
    sigma = initial_sigma

    # Newton-Raphson iterations
    for iteration in range(max_iterations):
        print(f"Itération {iteration + 1} : sigma = {sigma:.10f}")

        # Calculate theoretical price
        theoretical_price = black_scholes_call(
            S0, K, T, r, sigma
        )

        # Calculate pricing error
        error = theoretical_price - market_price

        # Convergence condition
        if abs(error) < tolerance:
            return float(sigma)

        # Calculate Vega
        vega_value = vega(S0, K, T, r, sigma)

        # Avoid division by a very small Vega
        if abs(vega_value) < 1e-12:
            raise ValueError(
                "Vega is too small. Newton-Raphson cannot continue."
            )

        # Newton-Raphson update
        sigma_new = sigma - error / vega_value

        # Volatility must remain positive
        if sigma_new <= 0:
            raise ValueError(
                "Newton-Raphson produced a non-positive volatility."
            )

        sigma = sigma_new

    raise RuntimeError(
        "Newton-Raphson did not converge."
    )

def implied_volatility_put(
    market_price,
    S0,
    K,
    T,
    r,
    initial_sigma=0.20,
    tolerance=1e-8,
    max_iterations=100
):
    """
    Calculate the implied volatility of a European Put
    using the Newton-Raphson method.
    """

    sigma = initial_sigma

    for iteration in range(max_iterations):

        print(f"Itération {iteration + 1} : sigma = {sigma:.10f}")

        # Calcul du prix théorique du Put
        theoretical_price = black_scholes_put(
            S0, K, T, r, sigma
        )

        # Erreur de prix
        error = theoretical_price - market_price

        # Condition de convergence
        if abs(error) < tolerance:
            return float(sigma)

        # Calcul du Vega
        vega_value = vega(S0, K, T, r, sigma)

        if abs(vega_value) < 1e-12:
            raise ValueError(
                "Vega is too small. Newton-Raphson cannot continue."
            )

        # Mise à jour de Newton-Raphson
        sigma_new = sigma - error / vega_value

        if sigma_new <= 0:
            raise ValueError(
                "Newton-Raphson produced a non-positive volatility."
            )

        sigma = sigma_new

    raise RuntimeError(
        "Newton-Raphson did not converge."
    )
