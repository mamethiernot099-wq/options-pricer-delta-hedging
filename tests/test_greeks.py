
import unittest

from src.greeks import (
    delta_call,
    delta_put,
    gamma,
    vega,
    theta_call,
    theta_put,
    rho_call,
    rho_put,
    calculate_greeks
)


class TestGreeks(unittest.TestCase):

    def setUp(self):
        # Paramètres communs
        self.S0 = 100
        self.K = 100
        self.T = 1
        self.r = 0.05
        self.sigma = 0.20

    # --------------------------------------------------
    # 1. DELTA
    # --------------------------------------------------

    def test_delta_call_range(self):
        result = delta_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)
        self.assertLess(result, 1)

    def test_delta_put_range(self):
        result = delta_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, -1)
        self.assertLess(result, 0)

    def test_put_call_delta_parity(self):
        dc = delta_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        dp = delta_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(dc - dp, 1.0, places=10)

    # --------------------------------------------------
    # 2. GAMMA
    # --------------------------------------------------

    def test_gamma_is_positive(self):
        result = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)

    def test_gamma_call_put_equality(self):
        # Black-Scholes : même Gamma pour Call et Put
        gc = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        gp = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(gc, gp, places=12)

    # --------------------------------------------------
    # 3. VEGA
    # --------------------------------------------------

    def test_vega_is_positive(self):
        result = vega(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)

    # --------------------------------------------------
    # 4. THETA
    # --------------------------------------------------

    def test_theta_call_value(self):
        result = theta_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(
            result, -6.414027546438197, places=10
        )

    def test_theta_put_value(self):
        result = theta_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(
            result, -1.657880423934626, places=10
        )

    # --------------------------------------------------
    # 5. RHO
    # --------------------------------------------------

    def test_rho_call_is_positive(self):
        result = rho_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)

    def test_rho_put_is_negative(self):
        result = rho_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertLess(result, 0)

    # --------------------------------------------------
    # 6. CALCULATE_GREEKS
    # --------------------------------------------------

    def test_calculate_greeks_call(self):
        result = calculate_greeks(
            self.S0, self.K, self.T,
            self.r, self.sigma, "call"
        )

        expected_keys = {
            "Delta", "Gamma", "Vega", "Theta", "Rho"
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_calculate_greeks_put(self):
        result = calculate_greeks(
            self.S0, self.K, self.T,
            self.r, self.sigma, "put"
        )

        expected_keys = {
            "Delta", "Gamma", "Vega", "Theta", "Rho"
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_calculate_greeks_invalid_type(self):
        with self.assertRaises(ValueError):
            calculate_greeks(
                self.S0, self.K, self.T,
                self.r, self.sigma, "invalid"
            )


if __name__ == "__main__":
    unittest.main()

