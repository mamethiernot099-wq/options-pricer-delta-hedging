
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
        self.S0 = 100
        self.K = 100
        self.T = 1
        self.r = 0.05
        self.sigma = 0.20

    def test_delta_call_put_parity(self):
        dc = delta_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        dp = delta_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(dc - dp, 1.0, places=10)

    def test_gamma_is_positive(self):
        result = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)

    def test_vega_is_positive(self):
        result = vega(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(result, 0)

    def test_theta_call_put(self):
        tc = theta_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        tp = theta_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertLess(tc, 0)
        self.assertLess(tp, 0)

    def test_rho_call_put(self):
        rc = rho_call(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        rp = rho_put(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertGreater(rc, 0)
        self.assertLess(rp, 0)

    def test_gamma_call_put_equality(self):
        gc = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )
        gp = gamma(
            self.S0, self.K, self.T, self.r, self.sigma
        )

        self.assertAlmostEqual(gc, gp, places=12)

    def test_calculate_greeks(self):
        call = calculate_greeks(
            self.S0, self.K, self.T,
            self.r, self.sigma, "call"
        )

        put = calculate_greeks(
            self.S0, self.K, self.T,
            self.r, self.sigma, "put"
        )

        self.assertEqual(
            set(call.keys()),
            {"Delta", "Gamma", "Vega", "Theta", "Rho"}
        )

        self.assertEqual(set(call.keys()), set(put.keys()))

    def test_invalid_option_type(self):
        with self.assertRaises(ValueError):
            calculate_greeks(
                self.S0, self.K, self.T,
                self.r, self.sigma, "invalid"
            )


if __name__ == "__main__":
    unittest.main()
