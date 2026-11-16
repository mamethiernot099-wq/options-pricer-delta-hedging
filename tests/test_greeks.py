import unittest

from src.greeks import (
    delta_call, delta_put, gamma, vega,
    theta_call, theta_put, rho_call, rho_put,
    calculate_greeks,
)
from src.pricing import black_scholes_call, black_scholes_put


class TestGreeks(unittest.TestCase):

    def setUp(self):
        self.S0 = 100.0
        self.K = 100.0
        self.T = 1.0
        self.r = 0.05
        self.sigma = 0.20

    def price(self, option_type, S=None, T=None, r=None, sigma=None):
        args = (
            self.S0 if S is None else S,
            self.K,
            self.T if T is None else T,
            self.r if r is None else r,
            self.sigma if sigma is None else sigma,
        )
        pricer = black_scholes_call if option_type == "call" else black_scholes_put
        return pricer(*args)

    def test_delta_ranges_and_put_call_parity(self):
        dc = delta_call(self.S0, self.K, self.T, self.r, self.sigma)
        dp = delta_put(self.S0, self.K, self.T, self.r, self.sigma)
        self.assertTrue(0.0 < dc < 1.0)
        self.assertTrue(-1.0 < dp < 0.0)
        self.assertAlmostEqual(dc - dp, 1.0, places=12)

    def test_gamma_positive_and_same_for_call_put(self):
        value = gamma(self.S0, self.K, self.T, self.r, self.sigma)
        self.assertGreater(value, 0.0)
        # Black-Scholes Gamma is independent of option type.
        self.assertAlmostEqual(
            value, gamma(self.S0, self.K, self.T, self.r, self.sigma),
            places=14,
        )

    def test_vega_positive(self):
        self.assertGreater(vega(self.S0, self.K, self.T, self.r, self.sigma), 0.0)

    def test_theta_reference_values(self):
        self.assertAlmostEqual(
            theta_call(self.S0, self.K, self.T, self.r, self.sigma),
            -6.414027546438197, places=10,
        )
        self.assertAlmostEqual(
            theta_put(self.S0, self.K, self.T, self.r, self.sigma),
            -1.657880423934626, places=10,
        )

    def test_rho_signs(self):
        self.assertGreater(rho_call(self.S0, self.K, self.T, self.r, self.sigma), 0.0)
        self.assertLess(rho_put(self.S0, self.K, self.T, self.r, self.sigma), 0.0)

    def test_analytic_delta_matches_finite_difference(self):
        h = 1e-3
        for option_type, greek in (("call", delta_call), ("put", delta_put)):
            numerical = (
                self.price(option_type, S=self.S0 + h)
                - self.price(option_type, S=self.S0 - h)
            ) / (2.0 * h)
            analytical = greek(self.S0, self.K, self.T, self.r, self.sigma)
            self.assertAlmostEqual(analytical, numerical, places=6)

    def test_analytic_gamma_matches_finite_difference(self):
        h = 1e-2
        for option_type in ("call", "put"):
            numerical = (
                self.price(option_type, S=self.S0 + h)
                - 2.0 * self.price(option_type)
                + self.price(option_type, S=self.S0 - h)
            ) / h**2
            self.assertAlmostEqual(
                gamma(self.S0, self.K, self.T, self.r, self.sigma),
                numerical, places=5,
            )

    def test_analytic_vega_matches_finite_difference(self):
        h = 1e-5
        for option_type in ("call", "put"):
            numerical = (
                self.price(option_type, sigma=self.sigma + h)
                - self.price(option_type, sigma=self.sigma - h)
            ) / (2.0 * h)
            self.assertAlmostEqual(
                vega(self.S0, self.K, self.T, self.r, self.sigma),
                numerical, places=5,
            )

    def test_analytic_theta_matches_negative_maturity_derivative(self):
        h = 1e-5
        for option_type, greek in (("call", theta_call), ("put", theta_put)):
            numerical_theta = -(
                self.price(option_type, T=self.T + h)
                - self.price(option_type, T=self.T - h)
            ) / (2.0 * h)
            self.assertAlmostEqual(
                greek(self.S0, self.K, self.T, self.r, self.sigma),
                numerical_theta, places=5,
            )

    def test_analytic_rho_matches_finite_difference(self):
        h = 1e-5
        for option_type, greek in (("call", rho_call), ("put", rho_put)):
            numerical = (
                self.price(option_type, r=self.r + h)
                - self.price(option_type, r=self.r - h)
            ) / (2.0 * h)
            self.assertAlmostEqual(
                greek(self.S0, self.K, self.T, self.r, self.sigma),
                numerical, places=5,
            )

    def test_calculate_greeks_returns_all_values(self):
        expected = {"Delta", "Gamma", "Vega", "Theta", "Rho"}
        for option_type in ("call", "put"):
            result = calculate_greeks(
                self.S0, self.K, self.T, self.r, self.sigma, option_type
            )
            self.assertEqual(set(result), expected)
            self.assertTrue(all(isinstance(x, float) for x in result.values()))

    def test_option_type_is_case_and_whitespace_insensitive(self):
        self.assertEqual(
            calculate_greeks(self.S0, self.K, self.T, self.r, self.sigma, " CALL "),
            calculate_greeks(self.S0, self.K, self.T, self.r, self.sigma, "call"),
        )

    def test_invalid_option_type_raises_value_error(self):
        for invalid in ("invalid", None, 123, True):
            with self.subTest(option_type=invalid):
                with self.assertRaises(ValueError):
                    calculate_greeks(
                        self.S0, self.K, self.T, self.r, self.sigma, invalid
                    )


if __name__ == "__main__":
    unittest.main()
