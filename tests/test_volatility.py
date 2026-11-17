import unittest

from src.pricing import black_scholes_call, black_scholes_put
from src.volatility import implied_volatility_call, implied_volatility_put


class TestImpliedVolatility(unittest.TestCase):

    def setUp(self):
        self.S0 = 100.0
        self.K = 100.0
        self.T = 1.0
        self.r = 0.05

    def test_implied_volatility_call(self):
        true_sigma = 0.25
        market_price = black_scholes_call(
            self.S0, self.K, self.T, self.r, true_sigma
        )
        implied_sigma = implied_volatility_call(
            market_price, self.S0, self.K, self.T, self.r,
            initial_sigma=0.20,
        )
        self.assertAlmostEqual(implied_sigma, true_sigma, places=7)

    def test_implied_volatility_put(self):
        true_sigma = 0.30
        market_price = black_scholes_put(
            self.S0, self.K, self.T, self.r, true_sigma
        )
        implied_sigma = implied_volatility_put(
            market_price, self.S0, self.K, self.T, self.r,
            initial_sigma=0.20,
        )
        self.assertAlmostEqual(implied_sigma, true_sigma, places=7)

    def test_call_and_put_recover_low_and_high_volatility(self):
        for true_sigma in (0.05, 0.15, 0.50, 1.20):
            with self.subTest(sigma=true_sigma):
                call_price = black_scholes_call(
                    self.S0, self.K, self.T, self.r, true_sigma
                )
                put_price = black_scholes_put(
                    self.S0, self.K, self.T, self.r, true_sigma
                )
                self.assertAlmostEqual(
                    implied_volatility_call(
                        call_price, self.S0, self.K, self.T, self.r
                    ),
                    true_sigma, places=6,
                )
                self.assertAlmostEqual(
                    implied_volatility_put(
                        put_price, self.S0, self.K, self.T, self.r
                    ),
                    true_sigma, places=6,
                )

    def test_invalid_market_prices_are_rejected(self):
        # For these parameters, the Call bounds are (S0 - K exp(-rT), S0).
        for bad_price in (-1.0, 0.0, self.S0):
            with self.subTest(price=bad_price):
                with self.assertRaises(ValueError):
                    implied_volatility_call(
                        bad_price, self.S0, self.K, self.T, self.r
                    )

    def test_invalid_solver_parameters_are_rejected(self):
        market_price = black_scholes_call(
            self.S0, self.K, self.T, self.r, 0.2
        )
        invalid_arguments = (
            {"initial_sigma": 0.0},
            {"initial_sigma": float("nan")},
            {"tolerance": 0.0},
            {"tolerance": float("inf")},
            {"max_iterations": 0},
            {"max_iterations": 1.5},
            {"max_iterations": True},
        )
        for kwargs in invalid_arguments:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    implied_volatility_call(
                        market_price, self.S0, self.K, self.T, self.r,
                        **kwargs,
                    )

    def test_non_numeric_market_price_is_rejected(self):
        with self.assertRaises(ValueError):
            implied_volatility_call(
                "not-a-price", self.S0, self.K, self.T, self.r
            )

    def test_zero_iteration_budget_is_rejected(self):
        market_price = black_scholes_put(
            self.S0, self.K, self.T, self.r, 0.3
        )
        with self.assertRaises(ValueError):
            implied_volatility_put(
                market_price, self.S0, self.K, self.T, self.r,
                max_iterations=0,
            )


if __name__ == "__main__":
    unittest.main()
