#!/usr/bin/python
# coding: utf-8

from common import *
import urllib
import re

from tools.post import updateArticle, MuseArticle
from poster import addComment


# class Post_test(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         destroy()
#         init()

#         # Post dummy
#         updateArticle(Var.dummy_id)

#     @classmethod
#     def tearDownClass(cls):
#         destroy()

class Test_ (TestCase):
    @classmethod
    def setUpClass(cls): pass
    @classmethod
    def tearDownClass(cls): pass
    

class Comment_test(TestCase):

    @classmethod
    def setUpClass(cls):
        destroy()
        init()

    @classmethod
    def tearDownClass(cls):
        destroy()

    def setUp(self):
        # Post dummy
        updateArticle(Var.dummy_id)
    
    def tearDown(self): pass



    def posting_comment(self):
        # Let's post comment
        content = 'akkccunnnt'
        pre_query = {'doc_id': Var.dummy_id,
                     'content': content}
        query = urllib.urlencode(pre_query)
        url = config.url_root + 'poster.py?' + query

        b = get_browser()
        b.go(url)

        # find will return -1 when no match, other is the possition
        web_content = b.get_html()
        assert web_content.find(content) != -1

    def limiting_comment(self):
        '''
        The tag can limit the number of comment of the article.
        '''
        counts = 3
        # Let's post comment
        content = 'akkccunnnt'
        pre_query = {'doc_id': Var.dummy_id,
                     'content': content}
        for count in range(counts):
            pre_query['content'] = content + str(count)
            query = urllib.urlencode(pre_query)
            url = config.url_root + 'poster.py?' + query

            b = get_browser()
            b.go(url)

        url = config.url_root + 'server.py?id=' + Var.dummy_id
        b.go(url)
        web_content = b.get_html()
        # We can find only 0, 1, 2. Because dummy's climit tag is 3.
        assert web_content.find(content + str(counts - 1)) != -1
        assert web_content.find(content + str(counts)) == -1


    def articleHooking_homeChar(self):
        '''
        config.py ArticleHook has a problem. We couldn't replace '~'
        character.
        '''
        dummy_id = Var.dummy_id
        # The text will be "files/image2099.jpg"
        text_willbe_changed = "~/.emacs.d/imgs/image2099.jpg"        
        article = MuseArticle(dummy_id)
        content = article.getHtml()
        
        matchobj = re.match(content, text_willbe_changed)
        assert matchobj != 0

