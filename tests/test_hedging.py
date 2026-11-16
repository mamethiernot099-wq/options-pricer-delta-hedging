import unittest

import numpy as np

from src.hedging import (
    simulate_gbm_path,
    calculate_call_delta,
    delta_hedging_simulation,
)


class TestHedging(unittest.TestCase):

    def setUp(self):
        self.S0, self.K, self.T = 100.0, 100.0, 1.0
        self.r, self.sigma = 0.05, 0.20

    def test_gbm_initial_price_and_path_length(self):
        times, prices = simulate_gbm_path(
            self.S0, self.r, self.sigma, self.T, n_steps=252, seed=42
        )
        self.assertEqual(len(prices), 253)
        self.assertEqual(len(times), 253)
        self.assertEqual(prices[0], self.S0)
        self.assertAlmostEqual(times[-1], self.T)

    def test_gbm_reproducibility(self):
        _, first = simulate_gbm_path(
            self.S0, self.r, self.sigma, self.T, seed=42
        )
        _, second = simulate_gbm_path(
            self.S0, self.r, self.sigma, self.T, seed=42
        )
        np.testing.assert_array_equal(first, second)

    def test_gbm_prices_are_positive_and_finite(self):
        _, prices = simulate_gbm_path(
            self.S0, self.r, self.sigma, self.T, seed=7
        )
        self.assertTrue(np.isfinite(prices).all())
        self.assertTrue((prices > 0).all())

    def test_invalid_gbm_step_count(self):
        for steps in (0, -1, 1.5, True):
            with self.subTest(steps=steps):
                with self.assertRaises(ValueError):
                    simulate_gbm_path(self.S0, self.r, self.sigma, self.T, steps)

    def test_call_delta_reference_and_bounds(self):
        value = calculate_call_delta(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        self.assertAlmostEqual(value, 0.6368306512, places=8)
        self.assertTrue(0.0 <= value <= 1.0)

    def test_call_delta_at_expiry(self):
        self.assertEqual(calculate_call_delta(105, 100, 0, self.r, self.sigma), 1.0)
        self.assertEqual(calculate_call_delta(95, 100, 0, self.r, self.sigma), 0.0)
        self.assertEqual(calculate_call_delta(100, 100, 0, self.r, self.sigma), 0.5)

    def test_hedging_length_and_initial_value_without_costs(self):
        result = delta_hedging_simulation(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_steps=252, seed=42,
        )
        self.assertEqual(len(result), 253)
        self.assertAlmostEqual(result.iloc[0]["portfolio_value"], 0.0)
        self.assertTrue(np.isfinite(result["portfolio_value"]).all())

    def test_rebalancing_frequencies(self):
        expected_counts = {"daily": 251, "weekly": 50, "monthly": 11}
        for frequency, expected in expected_counts.items():
            with self.subTest(frequency=frequency):
                result = delta_hedging_simulation(
                    self.S0, self.K, self.T, self.r, self.sigma,
                    n_steps=252, seed=42,
                    rebalance_frequency=frequency,
                )
                # Includes the initial hedge, excludes the expiry date.
                self.assertEqual(int(result["rebalanced"].sum()), expected + 1)

    def test_transaction_costs_are_charged_and_accumulated(self):
        result = delta_hedging_simulation(
            self.S0, self.K, self.T, self.r, self.sigma,
            n_steps=252, seed=42, transaction_cost_bps=10.0,
        )
        self.assertGreater(result["cumulative_transaction_cost"].iloc[-1], 0.0)
        self.assertAlmostEqual(
            result["cumulative_transaction_cost"].iloc[-1],
            result["transaction_cost"].sum(),
        )
        self.assertLess(result["portfolio_value"].iloc[0], 0.0)

    def test_invalid_frequency_and_transaction_costs(self):
        with self.assertRaises(ValueError):
            delta_hedging_simulation(
                self.S0, self.K, self.T, self.r, self.sigma,
                rebalance_frequency="yearly",
            )
        for cost in (-1.0, float("nan"), True):
            with self.subTest(cost=cost):
                with self.assertRaises(ValueError):
                    delta_hedging_simulation(
                        self.S0, self.K, self.T, self.r, self.sigma,
                        transaction_cost_bps=cost,
                    )


if __name__ == "__main__":
    unittest.main()
