import math
import unittest

from rolling_window_utils import RollingWindow, InvalidWindowError


class TestConstruction(unittest.TestCase):

    def test_zero_capacity_rejected(self):
        with self.assertRaises(InvalidWindowError):
            RollingWindow(0)

    def test_negative_capacity_rejected(self):
        with self.assertRaises(InvalidWindowError):
            RollingWindow(-3)

    def test_non_int_capacity_rejected(self):
        with self.assertRaises(InvalidWindowError):
            RollingWindow(3.5)

    def test_bool_capacity_rejected(self):
        with self.assertRaises(InvalidWindowError):
            RollingWindow(True)


class TestEmpty(unittest.TestCase):

    def test_empty_mean_is_none(self):
        w = RollingWindow(3)
        self.assertIsNone(w.mean())

    def test_empty_peak_is_none(self):
        w = RollingWindow(3)
        self.assertIsNone(w.peak())

    def test_empty_trough_is_none(self):
        w = RollingWindow(3)
        self.assertIsNone(w.trough())

    def test_empty_values_is_empty_list(self):
        w = RollingWindow(3)
        self.assertEqual(w.values(), [])

    def test_empty_len_zero(self):
        w = RollingWindow(3)
        self.assertEqual(len(w), 0)


class TestBasic(unittest.TestCase):

    def test_push_returns_none(self):
        w = RollingWindow(3)
        self.assertIsNone(w.push(5))

    def test_mean_single_value(self):
        w = RollingWindow(3)
        w.push(10)
        self.assertEqual(w.mean(), 10.0)

    def test_mean_partial_fill(self):
        w = RollingWindow(5)
        w.push(2)
        w.push(4)
        w.push(6)
        self.assertEqual(w.mean(), 4.0)

    def test_peak_trough(self):
        w = RollingWindow(4)
        w.push(3)
        w.push(9)
        w.push(1)
        self.assertEqual(w.peak(), 9.0)
        self.assertEqual(w.trough(), 1.0)


class TestEviction(unittest.TestCase):

    def test_window_does_not_exceed_capacity(self):
        w = RollingWindow(3)
        for v in (1, 2, 3, 4, 5):
            w.push(v)
        self.assertEqual(w.values(), [3.0, 4.0, 5.0])
        self.assertEqual(len(w), 3)

    def test_mean_after_eviction(self):
        w = RollingWindow(3)
        for v in (1, 2, 3, 4, 5, 6):
            w.push(v)
        # window is [4, 5, 6]
        self.assertEqual(w.mean(), 5.0)

    def test_sum_does_not_drift_under_eviction(self):
        """The running sum must stay in sync with the buffer over many pushes."""
        w = RollingWindow(7)
        for v in range(-50, 51):
            w.push(v)
        expected = sum(range(44, 51))  # last 7 values: 44..50
        self.assertEqual(w.mean() * len(w), float(expected))


class TestInvalidInput(unittest.TestCase):

    def test_push_rejects_bool(self):
        w = RollingWindow(3)
        with self.assertRaises(InvalidWindowError):
            w.push(True)

    def test_push_rejects_string(self):
        w = RollingWindow(3)
        with self.assertRaises(InvalidWindowError):
            w.push("5")

    def test_push_rejects_nan(self):
        w = RollingWindow(3)
        with self.assertRaises(InvalidWindowError):
            w.push(float("nan"))

    def test_push_rejects_inf(self):
        w = RollingWindow(3)
        with self.assertRaises(InvalidWindowError):
            w.push(float("inf"))

    def test_push_rejects_negative_inf(self):
        w = RollingWindow(3)
        with self.assertRaises(InvalidWindowError):
            w.push(float("-inf"))


class TestFloats(unittest.TestCase):

    def test_mean_float_result(self):
        w = RollingWindow(2)
        w.push(1)
        w.push(2)
        self.assertAlmostEqual(w.mean(), 1.5)

    def test_negative_mean(self):
        w = RollingWindow(3)
        w.push(-10)
        w.push(-20)
        w.push(-30)
        self.assertEqual(w.mean(), -20.0)


class TestCapacityProperty(unittest.TestCase):

    def test_capacity_stored(self):
        w = RollingWindow(8)
        self.assertEqual(w.capacity, 8)

    def test_capacity_read_only(self):
        w = RollingWindow(8)
        with self.assertRaises(AttributeError):
            w.capacity = 4


if __name__ == "__main__":
    unittest.main()
