
import math
import unittest

from src.pricing import (
    black_scholes_call,
    black_scholes_put,
    monte_carlo_asian_call,
    monte_carlo_call,
    monte_carlo_call_antithetic
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



    # TEST 6 : Validation des paramètres numériques
    def test_rejects_non_numeric_parameters(self):
        with self.assertRaises(ValueError):
            black_scholes_call(
                "100", self.K, self.T, self.r, self.sigma
            )

    def test_rejects_non_finite_parameters(self):
        with self.assertRaises(ValueError):
            black_scholes_call(
                self.S0, self.K, self.T, float("nan"), self.sigma
            )

    def test_rejects_boolean_parameters(self):
        with self.assertRaises(ValueError):
            black_scholes_call(
                True, self.K, self.T, self.r, self.sigma
            )

    # TEST 7 : Validation du nombre de simulations
    def test_monte_carlo_rejects_invalid_simulation_count(self):
        for invalid_count in (1, 1.5, True):
            with self.subTest(n_simulations=invalid_count):
                with self.assertRaises(ValueError):
                    monte_carlo_call(
                        self.S0, self.K, self.T, self.r, self.sigma,
                        n_simulations=invalid_count
                    )

    # TEST 8 : Reproductibilité Monte-Carlo
    def test_monte_carlo_is_reproducible(self):
        first = monte_carlo_call(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_simulations=20_000, seed=123
        )
        second = monte_carlo_call(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_simulations=20_000, seed=123
        )
        self.assertEqual(first, second)

    # TEST 9 : Cohérence statistique de l'estimateur standard
    def test_monte_carlo_confidence_interval_contains_reference(self):
        reference = black_scholes_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        result = monte_carlo_call(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_simulations=200_000, seed=42
        )
        lower, upper = result["confidence_interval"]
        self.assertLessEqual(lower, reference)
        self.assertGreaterEqual(upper, reference)

    # TEST 10 : Cohérence statistique des variables antithétiques
    def test_antithetic_confidence_interval_contains_reference(self):
        reference = black_scholes_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        result = monte_carlo_call_antithetic(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_pairs=100_000, seed=42
        )
        lower, upper = result["confidence_interval"]
        self.assertLessEqual(lower, reference)
        self.assertGreaterEqual(upper, reference)


if __name__ == "__main__":
    unittest.main()
