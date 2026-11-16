
import unittest
import numpy as np

from src.hedging import (
    simulate_gbm_path,
    calculate_call_delta,
    delta_hedging_simulation
)


class TestHedging(unittest.TestCase):

    def test_gbm_initial_price(self):

        times, prices = simulate_gbm_path(
            100, 0.05, 0.20, 1,
            n_steps=252,
            seed=42
        )

        self.assertEqual(prices[0], 100)

    def test_gbm_path_length(self):

        times, prices = simulate_gbm_path(
            100, 0.05, 0.20, 1,
            n_steps=252,
            seed=42
        )

        self.assertEqual(len(prices), 253)
        self.assertEqual(len(times), 253)

    def test_gbm_reproducibility(self):

        _, prices1 = simulate_gbm_path(
            100, 0.05, 0.20, 1, seed=42
        )

        _, prices2 = simulate_gbm_path(
            100, 0.05, 0.20, 1, seed=42
        )

        np.testing.assert_array_equal(
            prices1, prices2
        )

    def test_call_delta(self):

        delta = calculate_call_delta(
            100, 100, 1, 0.05, 0.20
        )

        self.assertAlmostEqual(
            delta,
            0.6368306512,
            places=8
        )

    def test_call_delta_bounds(self):

        delta = calculate_call_delta(
            100, 100, 1, 0.05, 0.20
        )

        self.assertGreaterEqual(delta, 0)
        self.assertLessEqual(delta, 1)

    def test_delta_hedging_length(self):

        results = delta_hedging_simulation(
            100, 100, 1, 0.05, 0.20,
            n_steps=252,
            seed=42
        )

        self.assertEqual(len(results), 253)

    def test_delta_hedging_initial_pnl(self):

        results = delta_hedging_simulation(
            100, 100, 1, 0.05, 0.20,
            n_steps=252,
            seed=42
        )

        initial_pnl = results.iloc[0]["portfolio_value"]

        self.assertAlmostEqual(initial_pnl, 0.0)

    def test_delta_hedging_finite_pnl(self):

        results = delta_hedging_simulation(
            100, 100, 1, 0.05, 0.20,
            n_steps=252,
            seed=42
        )

        self.assertTrue(
            np.isfinite(
                results["portfolio_value"]
            ).all()
        )


if __name__ == "__main__":
    unittest.main()
