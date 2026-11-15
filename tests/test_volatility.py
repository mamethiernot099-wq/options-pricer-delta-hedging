
import unittest

from src.pricing import (
    black_scholes_call,
    black_scholes_put
)

from src.volatility import (
    implied_volatility_call,
    implied_volatility_put
)


class TestImpliedVolatility(unittest.TestCase):

    def setUp(self):
        self.S0 = 100
        self.K = 100
        self.T = 1
        self.r = 0.05

    def test_implied_volatility_call(self):

        true_sigma = 0.25

        market_price = black_scholes_call(
            self.S0,
            self.K,
            self.T,
            self.r,
            true_sigma
        )

        implied_sigma = implied_volatility_call(
            market_price,
            self.S0,
            self.K,
            self.T,
            self.r,
            initial_sigma=0.20
        )

        self.assertAlmostEqual(
            implied_sigma,
            true_sigma,
            places=7
        )

    def test_implied_volatility_put(self):

        true_sigma = 0.30

        market_price = black_scholes_put(
            self.S0,
            self.K,
            self.T,
            self.r,
            true_sigma
        )

        implied_sigma = implied_volatility_put(
            market_price,
            self.S0,
            self.K,
            self.T,
            self.r,
            initial_sigma=0.20
        )

        self.assertAlmostEqual(
            implied_sigma,
            true_sigma,
            places=7
        )


if __name__ == "__main__":
    unittest.main()
