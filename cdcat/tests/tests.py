import unittest

import cdcat

class TestCdcat(unittest.TestCase):

    # def test_twenty_four_seven(self):
    #     oh = OpeningHours('24/7')
    #     self.assertEqual(oh.getStateString(), 'open')
    #     self.assertTrue(oh.isWeekStable())

    #     oh = OpeningHours('open')
    #     self.assertEqual(oh.getStateString(), 'open')
    #     self.assertTrue(oh.isWeekStable())

    def test_invalid_value(self):
        True
    #     self.assertRaises(ParseException, OpeningHours, 'fail "not valid keyword"')
    #     self.assertRaises(ParseException, OpeningHours, ' ')

if __name__ == "__main__":
    unittest.main()
