
import math
import unittest

from src.pricing import (
    black_scholes_call,
    black_scholes_put,
    monte_carlo_asian_call
)


class TestBlackScholes(unittest.TestCase):

    def setUp(self):
        """
        Paramètres communs aux tests.
        """
        self.S0 = 100
        self.K = 100
        self.T = 1
        self.r = 0.05
        self.sigma = 0.20

    # TEST 1 : Prix du Call
    def test_call_price(self):

        call = black_scholes_call(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma
        )

        self.assertAlmostEqual(
            call,
            10.4506,
            places=4
        )

    # TEST 2 : Prix du Put
    def test_put_price(self):

        put = black_scholes_put(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma
        )

        self.assertAlmostEqual(
            put,
            5.5735,
            places=4
        )

    # TEST 3 : Parité Call-Put
    def test_put_call_parity(self):

        call = black_scholes_call(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma
        )

        put = black_scholes_put(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma
        )

        theoretical_value = (
            self.S0
            - self.K * math.exp(-self.r * self.T)
        )

        self.assertAlmostEqual(
            call - put,
            theoretical_value,
            places=10
        )

    # TEST 4 : Positivité du prix asiatique
    def test_asian_call_price_is_nonnegative(self):

        result = monte_carlo_asian_call(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma,
            n_simulations=10000,
            n_steps=252,
            seed=42
        )

        self.assertGreaterEqual(
            result["price"],
            0
        )

    # TEST 5 : Cohérence de l'intervalle de confiance
    def test_asian_call_confidence_interval(self):

        result = monte_carlo_asian_call(
            self.S0,
            self.K,
            self.T,
            self.r,
            self.sigma,
            n_simulations=10000,
            n_steps=252,
            seed=42
        )

        lower, upper = result["confidence_interval"]

        self.assertLessEqual(
            lower,
            result["price"]
        )

        self.assertGreaterEqual(
            upper,
            result["price"]
        )


if __name__ == "__main__":
    unittest.main()
