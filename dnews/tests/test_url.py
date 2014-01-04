from common import *
from unittest import TestCase

from dnews.url import generate_urls, product_generator, merge_lists, list_range_to_list

class Test_libs(TestCase):

    def test_generate_urls(self):
        url_format = 'http://example.com/%s/%s'
        url_range = [[range(4)], [range(1, 7), range(5, 9)]]
        self.assertEqual(list(generate_urls(url_format, url_range)), ['http://example.com/0/1', 'http://example.com/0/2', 'http://example.com/0/3', 'http://example.com/0/4', 'http://example.com/0/5', 'http://example.com/0/6', 'http://example.com/0/5', 'http://example.com/0/6', 'http://example.com/0/7', 'http://example.com/0/8', 'http://example.com/1/1', 'http://example.com/1/2', 'http://example.com/1/3', 'http://example.com/1/4', 'http://example.com/1/5', 'http://example.com/1/6', 'http://example.com/1/5', 'http://example.com/1/6', 'http://example.com/1/7', 'http://example.com/1/8', 'http://example.com/2/1', 'http://example.com/2/2', 'http://example.com/2/3', 'http://example.com/2/4', 'http://example.com/2/5', 'http://example.com/2/6', 'http://example.com/2/5', 'http://example.com/2/6', 'http://example.com/2/7', 'http://example.com/2/8', 'http://example.com/3/1', 'http://example.com/3/2', 'http://example.com/3/3', 'http://example.com/3/4', 'http://example.com/3/5', 'http://example.com/3/6', 'http://example.com/3/5', 'http://example.com/3/6', 'http://example.com/3/7', 'http://example.com/3/8'])

        url_format2 = 'aa/%s/%s/%s'
        url_range2 = [[range(2)], [range(1, 3), range(5, 7)], [range(2), range(4, 6)]]
        self.assertEqual(len(list(generate_urls(url_format2, url_range2))), 32)

        url_range = [['a', 'b'], ['dd', 'yy']]
        self.assertEqual(list(generate_urls(url_format, url_range)), ['http://example.com/a/d', 'http://example.com/a/d', 'http://example.com/a/y', 'http://example.com/a/y', 'http://example.com/b/d', 'http://example.com/b/d', 'http://example.com/b/y', 'http://example.com/b/y'])
    
    def test_product_generator(self):
        url_range = [[range(4)], [range(1, 7), range(5, 9)]]
        self.assertEqual(list(product_generator(url_range)), [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 5), (0, 6), (0, 7), (0, 8), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 5), (1, 6), (1, 7), (1, 8), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 5), (2, 6), (2, 7), (2, 8), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 5), (3, 6), (3, 7), (3, 8)])

        url_range2 = [range(4), [range(1, 7), range(5, 9)]]
        self.assertEqual(list(product_generator(url_range2)), list(product_generator(url_range)))


    def test_merge_lists(self):
        alist = range(8)
        self.assertEqual(merge_lists(alist), [0, 1, 2, 3, 4, 5, 6, 7])

    def test_list_range_to_list(self):
        import types
        url_range = [1, 10]
        url_range2 = [[1, 5]]
        url_range3 = [[1,4], [6, 8], [12, 18]]
        url_range4 = ["a", "b"]

        self.assertEqual(list_range_to_list(url_range), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(list_range_to_list(url_range2), [1, 2, 3, 4])
        self.assertEqual(list_range_to_list(url_range3), [1, 2, 3, 6, 7, 12, 13, 14, 15, 16, 17])

        #self.assertEqual(list_range_to_list(url_range4), 888)
        #self.assertRaises(ValueError, list_range_to_list, url_range4)
        # with self.assertRaises(ValueError):
        #     list_range_to_list(url_range4) == 888

        
class Test_Urls(TestCase):
    def test_basic(self):
        #urls = Urls("%s/%s", [[range(2)], [range(3)]])
        pass

        
        
