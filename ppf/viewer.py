#!/usr/bin/python
# coding: utf-8

import os
import config
import indexer
import install

from jinja2 import Environment, FileSystemLoader, Markup
import scrubber



class Var:
    http_header = "Content-type: text/html; charset=utf-8\n\n"
    page_not_found_msg = "We has no page %s"

#Obsolete
class View(object):
    '''
    >>> ve = View()
    >>> err_msg = "[Errno 2] No such file or directory: '/home/ptmono/public_html/0ttd/0ppf2/ppf/dbs/index.json' "
    '''
    def show(self, form):
        #GET method
        # if form.keys() == []:
        #     view_categoryobj = ViewCategory()
        #     print view_categoryobj.show()

        if form.keys() == []:
            try:
                view_home = ViewHome()
            except IOError, err:
                if self._checkArticleIndex(err):
                    # There is no index file
                    self._initArticleIndex()
                    return
                else:
                    print "Content-type: text/html; charset=utf-8\n\n"
                    print err
                    return

            print view_home.show()

        elif form.has_key('id'):
            doc_id = form.getfirst('id')
            if doc_id == 'all':
                view_all = ViewAll()
                print view_all.show()
            else:
                viewobj = ViewId(doc_id)
                print viewobj.show()

    def _checkArticleIndex(self, err_msg):
        msg = str(err_msg)
        if msg.find(config.index_file) == -1:
            return False
        return True

    def _initArticleIndex(self):
        # fd = file(config.index_filename(), 'w')
        # fd.write('{}')
        # fd.close()
        install.main()

class ViewAbstract(object):

    """
    >>> aa = indexer.Articles()
    >>> aa.set()
    >>> aa.json.keys() #doctest: +SKIP
    >>> aa.json #doctest: +SKIP
    """
    def __init__(self):
        self.jinja_env = Environment(loader=FileSystemLoader(config.medias_d))
        def sanitize_html(text):
            return Markup(scrubber.Scrubber(remove_comments=False).scrub(text))

        self.jinja_env.filters['sanitize_html'] = sanitize_html

        self.content = self.getContent()

    def show(self):
        result = ''
        #result += Var.http_header
        result += self.content
        return result

    def getContent(self):
        pass

    def getHeader(self):
        result = ''
        fd = file(config.html_header, 'r')
        result = fd.read()
        return result

    def getFooter(self):
        result = ''
        fd = file(config.html_footer, 'r')
        result = fd.read()
        return result

    def lastestDocNumber(self):
        "Returns lastest doc number"
        articles = indexer.Articles()
        articles.set()
        lastest_json = articles.indexes[-1]
        return lastest_json

    def lastestDocNumberPublished(self):
        ""
        articles = indexer.Articles()
        articles.set()
        # try:
        #     articles.indexes.reverse()
        # except:
        #     return '0000000000'

        for article in articles:
            if article.unpublished:
                continue
            return article.doc_id
        return '0000000000'
        

    def fileContentWithUnicode(self, filename, char_set=config.char_set):
        "Jinja requires unicode content. So have to read the file as unicode."
        fd = file(filename, 'r')
        content = fd.read()
        fd.close()
        # Jinja require unicode
        return content.decode(char_set)


class ViewAll(ViewAbstract):
    """

    >>> #aa = ViewAll()
    >>> #aa._getContent()

    """

    def getContent(self):
        result = ''
        article_info_l = self._getContent()
        temp_context = dict(article=article_info_l)

        # Render
        temp = self.jinja_env.get_template('jinja_list.html')
        result = temp.render(temp_context)

        # The result is unicode
        result = result.encode(config.char_set)
        return result

    def _getContent(self):
        # Get the rendered context 'temp_context
        article_info_l = []
        articles = indexer.Articles()
        articles.set()

        for article in articles:
            href = '/article/' + article.doc_id
            comments = indexer.Comments(article.doc_id)
            comments_count = len(comments)
            # We want only own tag.
            tag = article.tag.split(" ")[0]
            if article.unpublished:
                continue
            article_info_tup = (article.doc_id, article.title, tag, href, comments_count)
            article_info_l.append(article_info_tup)
        return article_info_l
        


class ViewId(ViewAbstract):

    """

    >>> #aa = ViewId('0705151524')
    >>> #aa.getComments()
    """
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self._check()
        super(ViewId, self).__init__()
        
    def getContent(self):
        result = ''
        html_f = config.htmls_d + str(self.doc_id) + ".html"
        try:
            temp_context = self.fileContentWithUnicode(html_f)
        except:
            return self._showPageNotFoundError()

        comments = self.getComments()

        temp = self.jinja_env.get_template('jinja_content.html')
        if comments:
            result = temp.render(content=temp_context, doc_id=self.doc_id, comments=comments)
        else:
            # There is no comment
            result = temp.render(content=temp_context, doc_id=self.doc_id)
        # Jinja requires unicode strings
        result = result.encode(config.char_set)
        return result

    def _showPageNotFoundError(self):
        content = Var.page_not_found_msg % self.doc_id
        #content = Var.http_header + '\n\n' + content
        return content

    def _check(self):
        "let's check for validate doc_id. doc_id is 10 dicimal number."
        try:
            int(self.doc_id)
        except:
            self._showPageNotFoundError()

    def getComments(self):
        comment_info_l = []
        try:
            comments = indexer.Comments()
            comments.set(self.doc_id)
        except IOError:
            return None
        for comment in comments:
            comment_info_l.append(comment)

        return comment_info_l



class ViewHome(ViewId):
    # Todo: Security problem. When a customer post the content can
    # contains javascript.

    def __init__(self):
        doc_id = self.lastestDocNumberPublished()
        super(ViewHome, self).__init__(doc_id)


    def getContent(self):
        result = ''
        html_f = os.path.join(config.htmls_d, str(self.doc_id) + ".html")
        try:
            temp_context = self.fileContentWithUnicode(html_f)
        except:
            #raise
            return self._showPageNotFoundError()

        comments = self.getComments()
        if comments:
            comments_info_l = self.getComments()
        else:
            comments_info_l = None


        #TODO: I want to allow <font>, <b> <i> tag for escaping
        temp = self.jinja_env.get_template('jinja_door.html')
        if comments_info_l:
            result = temp.render(content=temp_context, doc_id=self.doc_id, comments=comments_info_l)
        else:
            # There is no comment
            result = temp.render(content=temp_context, doc_id=self.doc_id)
        # Jinja requires unicode strings
        result = result.encode(config.char_set)
        return result


