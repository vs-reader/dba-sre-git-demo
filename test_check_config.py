import unittest

from check_config import validate


def example(small=80, large=150):
    return f"[small]\nmax_connections = {small}\n[large]\nmax_connections = {large}\n"


class ConfigTests(unittest.TestCase):
    def test_initial_values_pass(self):
        self.assertTrue(validate(example())[0])

    def test_200_for_both_rejects_small_only(self):
        valid, messages = validate(example(200, 200))
        self.assertFalse(valid)
        self.assertTrue(any(line.startswith("FAIL: db01") for line in messages))
        self.assertTrue(any(line.startswith("PASS: db02") for line in messages))

    def test_corrected_values_pass(self):
        self.assertTrue(validate(example(100, 200))[0])

    def test_boundaries_pass(self):
        self.assertTrue(validate(example(1, 1))[0])
        self.assertTrue(validate(example(100, 300))[0])

    def test_out_of_range_fails(self):
        for small, large in [(0, 150), (-1, 150), (101, 150), (80, 301)]:
            with self.subTest(small=small, large=large):
                self.assertFalse(validate(example(small, large))[0])

    def test_invalid_number_fails(self):
        for value in ["abc", "1.5", "true", ""]:
            with self.subTest(value=value):
                self.assertFalse(validate(example(value))[0])

    def test_missing_profile_fails(self):
        self.assertFalse(validate("[small]\nmax_connections = 80\n")[0])

    def test_unknown_profile_fails(self):
        self.assertFalse(validate(example() + "[other]\nmax_connections = 80\n")[0])

    def test_unknown_key_fails(self):
        self.assertFalse(validate(example() + "max_connection = 150\n")[0])

    def test_empty_and_malformed_fail(self):
        self.assertFalse(validate("")[0])
        self.assertFalse(validate("not an INI file")[0])

    def test_duplicate_profile_fails(self):
        self.assertFalse(validate(example() + "[small]\nmax_connections = 80\n")[0])

    def test_defaults_fail(self):
        self.assertFalse(validate("[DEFAULT]\nmax_connections = 80\n[small]\n[large]\n")[0])


if __name__ == "__main__":
    unittest.main()
