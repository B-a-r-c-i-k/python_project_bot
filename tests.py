import unittest
import requests
import config
import token_base
import pars
import item_base

class TestBot(unittest.TestCase):
    def test_connection(self):
        self.assertEqual(requests.get(
                'https://steamcommunity.com/market/pricehistory/?appid=' +
                "730" + '&market_hash_name=' +
                "Sticker%20%7C%20Vitality%20%7C%202020%20RMR",
                cookies=config.cookie).status_code, 200)

    def test_token(self):
        self.assertTrue("test" in token_base.token_base)
        self.assertFalse("random_token" in token_base.token_base)

    def test_update_item(self):
        self.assertFalse(pars.update_item("random_name"))
        self.assertTrue(pars.update_item("Clutch Case"))
        self.assertTrue(config.CNT_ITEMS > 0)

    def test_parse(self):
        pars.parse(5)
        self.assertTrue(config.CNT_ITEMS == 5)
        self.assertTrue(len(item_base.items) == 5)
        #high percent to add new element
        pars.update_item("Clutch Case")
        self.assertTrue(config.CNT_ITEMS == 6)
        self.assertTrue(len(item_base.items) == 6)

    def test_get_correct_from(self):
        self.assertEqual(pars.get_correct_form(["Clutch Case"]), ["Clutch%20Case"])


    def test_get_cnt_items(self):
        self.assertTrue(pars.get_cnt_items() > 17000)


if __name__ == "__main__":
    unittest.main()