#!/usr/bin/python
# coding: utf-8

from common import *

import json

from api import Data
from indexer import Article
from tools.post import writeArticle, updateIndex, \
    updateServerFile, deleteComment, writeComment, \
    updateArticle, updateFile, updateFileWithFtp


class Post_test(TestCase):

    @classmethod
    def setUpClass(cls):
        destroy()               # Remove pre-installed
        init()

    @classmethod
    def tearDownClass(cls):
        destroy()

    def test_writeArticles(self):

        doc_id = '1111111111'
        _base64_content = "열라 테스트"
        dd = writeArticle(doc_id, _base64_content)
        assert dd == '\nOK\n'

    def test_updateIndex(self):
        doc_id = '1111111111'
        _jsonBase64_dict = {'category': 'emacs planner',
                            'date': '1108170951',
                            'author': 'this is author',
                            'update': '1108170952',
                            'title': '가나다 우리는 사는 사람들 이 닫 다다. fjdksf kdsf ',
                            'doc_id': '1111111111'}
        dd = updateIndex(doc_id, _jsonBase64_dict)
        assert dd == '\nOK\n'

    def test_writeComment_deleteComment(self):
        doc_id = '1111111111'
        _base64_content = '어찌하다가 우리가 이런일에 \\n 아'
        _base64_name = '달수'
        password = '12'

        dd = writeComment(doc_id, _base64_content, _base64_name, password)
        assert dd == '\nOK\n'

        doc_id = '1111111111'
        comment_id = '1'

        dd = deleteComment(doc_id, comment_id)
        assert dd == '\nOK\n'

        dd = deleteComment(doc_id, comment_id)
        assert dd == '\nFalse\n'

    def test_updateFile(self):
        filename = 'bbk'
        _base64_content = 'abc'
        dd = updateFile(filename, _base64_content)
        assert dd == '\nOK\n'

        dd = updateFile(filename, _base64_content)
        assert dd == '\nFalse\n'

    # TODO: I need a method to identify the result of test_updateArticle.
    # One way is to add a error handling for updateArticle.
    def test_updateArticle(self):
        # Let's use dummy file
        doc_id = '9999999999'
        updateArticle(doc_id)

        # Client side index updated?
        fd = file(config.index_filename(), 'r')
        client_index = fd.read()
        fd.close()

        # Server side index updated?
        # Server side was tested in other member.

    def test_updateFileWithFtp(self):

        dummy2_name = 'dummy.py'
        dummy2_path = config.current_abpath + dummy2_name
        fd = file(dummy2_path, 'w')
        fd.write('dummy')
        fd.close()

        # Root directory uploading
        # Check absolute path
        dummy2_server_path = config.server_root_directory + '/' + dummy2_name
        updateFileWithFtp(dummy2_path)
        assert os.path.exists(dummy2_server_path) == True
        os.remove(dummy2_server_path)

        os.remove(dummy2_path)


class TestingTools_test(TestCase):
    @classmethod
    def setUpClass(cls):
        destroy()
        init()
        updateArticle(Var.dummy_id)
        # Write a comment for dummy article
        doc_id = Var.dummy_id
        _base64_content = '어찌하다가 우리가 이런일에 \\n 아'
        _base64_name = '달수'
        password = '12'
        writeComment(doc_id, _base64_content, _base64_name, password)
        
    @classmethod
    def tearDownClass(cls):
        destroy()

    def test_basic(self):
        b = get_browser()
        query = Data()
        query.cmd = 'articles_length'

        url = config.url_root + 'api.py?' + query.urlencode()
        b.go(url)
        result = b.get_html()
        # For Secure key. server is using secure key?
        self.assertNotEqual(result.find('Error'), -1)

        # For articles_length
        query.secure_key = config.SECURE_KEY
        url = config.url_root + 'api.py?' + query.urlencode()

        b.go(url)
        result = b.get_html()
        self.assertEqual(libs.removeBlank(result), '2')

        # For comments_length
        query.cmd = 'comments_length'
        query.doc_id = Var.dummy_id

        url = config.url_root + 'api.py?' + query.urlencode()
        b.go(url)
        result = b.get_html()
        self.assertEqual(libs.removeBlank(result), '1')

        # For article_json
        query.cmd = 'article_json'
        url = config.url_root + 'api.py?' + query.urlencode()
        b.go(url)
        result = b.get_html()
        # Get the index of the local dummy
        article = Article()
        article.set(Var.dummy_id)
        result = json.loads(libs.removeBlank(result))
        self.assertEqual(result['doc_id'], unicode(article.__dict__['doc_id']))

