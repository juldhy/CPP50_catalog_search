import math
import unittest
from unittest.mock import MagicMock, patch

from engine.tokenize import tokenize
from engine.index import search_index, SearchIndex
from engine.ranking import search, compute_score
from engine.suggest import suggest


class TestTokenize(unittest.TestCase):

    def test_tokenize(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize(",,"), [])
        self.assertEqual(tokenize("a"), [])
        self.assertEqual(tokenize("aa;bb"), [])
        self.assertEqual(tokenize("aAa ,BbB cccC"), ['aaa','bbb','cccc'])
        self.assertEqual(tokenize("Smashable screen for sensitive computer scientists"), ['smashable', 'screen', 'for', 'sensitive', 'computer', 'scientists'])


class TestRanking(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ranking(self):
        products = search("wireless keyboard", top_k=5)
        self.assertEqual(len(products), 5)
        for product in products:
            tokens = tokenize(product['name']) + product['tags']
            self.assertIn("wireless", tokens) or self.assertIn("keyboard", tokens)

        products = search("wireless", top_k=10)
        for product in products:
            tokens = tokenize(product['name']) + product['tags']
            self.assertIn("wireless", tokens)

    def test_ranking_top_k(self):
        products = search("wireless keyboard", top_k=0)
        self.assertEqual(len(products), 0)

        products = search("wireless keyboard", top_k=-1)
        self.assertEqual(len(products), 0)

        query_tokens = search_index.index.keys()
        products = search(" ".join(query_tokens), top_k=len(search_index.catalog))
        self.assertEqual(len(products), len(search_index.catalog))
        self.assertEqual(products, sorted(products, key=lambda x:compute_score(x,set(query_tokens)), reverse=True))

        query_tokens = set(list(search_index.index.keys())[0:3])
        products = search(" ".join(query_tokens), top_k=5000)
        self.assertLessEqual(3, len(products))
        self.assertGreaterEqual(5000, len(products))
        self.assertEqual(products, sorted(products, key=lambda x:compute_score(x,query_tokens), reverse=True))


    def test_score(self):
        self.assertEqual(0, compute_score({'name': '', 'tags':[], 'stock':0, 'sales_rank':0}, set()), 0)
        self.assertEqual(0.3, compute_score({'name': '', 'tags': [], 'stock': 0, 'sales_rank': 0}, {'hdmi'}))
        self.assertEqual(0.5, compute_score({'name': '', 'tags': [], 'stock': 1, 'sales_rank': 0}, {'hdmi'}))
        self.assertEqual(1 / math.log2(1 + 2) * 0.3, compute_score({'name': '', 'tags': [], 'stock': 0, 'sales_rank': 1}, {'hdmi'}))
        self.assertEqual(0.8, compute_score({'name': 'hdmi', 'tags': [], 'stock': 0, 'sales_rank': 0}, {'hdmi'}))
        self.assertEqual(0.8, compute_score({'name': '', 'tags': ['hdmi'], 'stock': 0, 'sales_rank': 0}, {'hdmi'}))
        self.assertEqual(0.8, compute_score({'name': 'hdmi bus', 'tags': [], 'stock': 0, 'sales_rank': 0}, {'hdmi'}))
        self.assertEqual(0.55, compute_score({'name': 'hdmi', 'tags': ['driver'], 'stock': 0, 'sales_rank': 0}, {'hdmi', 'cable'}))


class TestIndex(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_catalog_size(self):
        # Knowing the size of the input catalog file, verify it is loaded correctly
        self.assertEqual(len(search_index.catalog), 5000)

    def test_search_index_coherency(self):
        # For each index entry, verify the referred products holds the entry as a token in its name or tags
        for token, product_ids in search_index.index.items():
            for product_id in product_ids:
                self.assertTrue(
                    token in search_index.catalog[product_id]['name'].lower()
                    or token in list(map(str.lower, search_index.catalog[product_id]['tags'])))

    def test_search_index_keys(self):
        # Each index entry has a length of at least 2 characters
        for token in search_index.index.keys():
            self.assertGreater(len(token), 2)
            self.assertTrue(token.islower())


class TestCategories(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_categories(self):
        pass


class TestSuggest(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        self.test_lexicon = list({'webcom': [], 'webcam': [], 'keyboard': []}.keys())

    def tearDown(self):
        pass

    def test_suggest_single_word(self):
        global search_index
        print(f"NB: Testing suggest() with index tokens = {self.test_lexicon}")
        self.assertEqual(3, len(self.test_lexicon ), msg="Incorrect test premises")
        self.assertIn('keyboard', self.test_lexicon, msg="Incorrect test premises")
        self.assertEqual(["keyboard"], suggest("keybaord", lexicon=self.test_lexicon) )
        self.assertEqual([], suggest("kebaord", lexicon=self.test_lexicon))
        self.assertEqual([], suggest("kebaorg", lexicon=self.test_lexicon))
        self.assertEqual(['keyboard'], suggest("keyboard",  lexicon=self.test_lexicon))
        self.assertEqual([], suggest("computer",  lexicon=self.test_lexicon))

        self.assertIn('webcam', self.test_lexicon, msg="Incorrect test premises")
        self.assertIn('webcom', self.test_lexicon, msg="Incorrect test premises")
        self.assertEqual(['webcam'], suggest("Webcm", 1, lexicon=self.test_lexicon), msg="here")
        self.assertEqual(['webcam', 'webcom'], suggest("wabcam",  lexicon=self.test_lexicon))
        self.assertEqual(['webcam'], suggest("webcame", 1,  lexicon=self.test_lexicon))

        # test default lexicon (uses ../catalog.json)
        print(f"NB: Testing suggest() with default index tokens = {search_index.get_index_tokens()}")
        self.assertEqual(['hub', 'usb'], suggest("ub", 2))

    def test_suggest_multiple_words(self):
        self.assertEqual(["keyboard"], suggest("keyborad",  lexicon=self.test_lexicon))

    def test_suggest_limit_cases(self):
        self.assertEqual([], suggest("",  lexicon=self.test_lexicon))
        self.assertEqual([], suggest("keyborad", 0,  lexicon=self.test_lexicon))
        self.assertEqual(['keyboard'], suggest("keyboard", 10,  lexicon=self.test_lexicon))


if __name__ == '__main__':
    unittest.main()