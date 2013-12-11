#!/usr/bin/python
# coding: utf-8

#TODO: We need secure method and more reusable way

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.header import Header

import time, os
import sys
import cgi
#from web.utils import sendmail
import config

#if config.LOCAL_TEST:
import cgitb
cgitb.enable()

from flask import request

import libs
from indexer import Comments, Comment, Articles, File

import html_messages as hm

def addComment(doc_id, form):
    comments = Comments()
    comments.set(doc_id)
    # We has the limit of the count of comment. The default is
    # config.max_comments.
    if not canComments(doc_id, comments):
        print "Content-type: text/html\n"
        print hm.redirect_error_limit_comments % doc_id
        return

    # Save comment
    comment = Comment()
    comment.doc_id = doc_id
    for key in form.keys():
        setattr(comment, key, form[key].value)
    comment.date = time.strftime("%m/%d|%y", time.localtime())
    comment.name = prepareName(comment.name)
    comment.password = preparePassword(comment.password)
    comment.content = prepareContent(comment.content)
    # updateFormObj will add the comment_id attribute to comment
    comments.updateFromObj(comment)
    comments.save()

    try:
        # Newly created comment key. Write to recentdb
        comment_key = comments.indexes[0]
        comment_id = doc_id + comment_key
        fd = File(None, 'rc', 'a')
        fd.write(comment_id)
        fd.close()
    except Exception, err:
        config.logger.error(err)



    # Send notification mail
    try:
        if config.comment_mail_me: sendMail(comment)
    except:
        msg = "Falied to send mail, comment_id %s" % comment_id
        config.logger.error(msg)
        
    print "Content-type: text/html\n"
    print hm.redirect % (doc_id + "#" + comment.comment_id)

def addComment_wsgi(request):
    # Form is werkzeug's ImmutableMultiDict
    form = request.form
    doc_id = form['doc_id']
    
    comments = Comments()
    comments.set(doc_id)
    if not canComments(doc_id, comments):
        return hm.redirect_error_limit_comments % doc_id

    comment = Comment()
    comment.setFromDict(form)
    comment.date = time.strftime("%m/%d|%y", time.localtime())
    comment.name = prepareName(comment.name)
    comment.password = preparePassword(comment.password)
    comment.content = prepareContent(comment.content)
    # updateFormObj will add the comment_id attribute to comment
    comments.updateFromObj(comment)
    comments.save()

    try:
        # Newly created comment key. Write to recentdb
        comment_key = comments.indexes[0]
        comment_id = doc_id + comment_key
        fd = File(None, 'rc', 'a')
        fd.write(comment_id)
        fd.close()
    except Exception, err:
        config.logger.error(err)

    # Send notification mail
    try:
        if config.comment_mail_me: sendMail(comment)
    except:
        msg = "Falied to send mail, comment_id %s" % comment_id
        config.logger.error(msg)
        
    return hm.redirect % (doc_id + "#" + comment.comment_id)

    
def canComments(doc_id, comments):
    '''
    Check the restricted count of the comment of document.
    doc_id: document number
    comments: an object of Comments
    '''
    # Check the limit of count of the comment
    comment_count = len(comments)
    limit = specified_limit_comments(doc_id)
    if not limit: limit = config.max_comments
    try:
        if comment_count >= int(limit):
            return False
    except:
        # config.max_comments is '' or can be int()
        pass
    return True

def prepareContent(content):
    max_size_of_content = 30000
    # Limit the size of content
    content = libs.strcut_utf8(content, max_size_of_content)
    return content.replace('\n', '<br>')

def prepareName(name):
    max_size_of_name = 25
    # Limit the size of name
    name = libs.strcut_utf8(name, max_size_of_name)
    return name

preparePassword = prepareName


def specified_limit_comments(doc_id):
    # TODO: It is so inefficient that every time we have to read all index
    # file.
    articles = Articles()
    articles.set()
    article = articles.article(doc_id)
    try:
        return article.climit
    except AttributeError:
        return config.max_comments


def sendMail(comment):
    "Notify the comment to the admin."
    #TODO: sendmail of web.py can be used. But it seems slow. I think to
    #use new thread is better.
    #sendMailUsingSendmail(obj)
    cm = CommentMailer(comment, config.mail_client)
    cm.send()


#TODO: 9 It seems slow like using web.utils. Consider a way which not use
#smtp.
class CommentMailer(object):
    """
    comment: comment object
    smtp: smtp type

    >>> comment = Comment()
    >>> comment.doc_id = '1109012200'
    >>> comment.comment_id = '11'
    >>> comment.title = 'ttitle'
    >>> comment.date = '32'
    >>> comment.content = 'ccontent'
    >>> cm = CommentMailer(comment, smtp='local')
    >>> cm.send()

    """
    def __init__(self, comment, smtp='local'):
        self.comment = comment
        self.smtp = smtp
        self.outer = MIMEMultipart()

    def attachText(self, text):
        try:
            data = MIMEText(text)
        except UnicodeEncodeError:
            data = MIMEText(text.encode(sys.getfilesystemencoding()))
        self.outer.attach(data)

    def attachImage(self, image):
        data = MIMEImage(image)
        self.outer.attach(data)

    def send(self):
        self.setFormat()
        if self.smtp == 'gmail': self._sendWithGmail()
        elif self.smtp == 'local': self._sendWithLocal()
        elif self.smtp == 'file': self._sendWithFile()

    def setFormat(self):
        # subject_length = 30
        # subject = libs.strcut_utf8(self.comment.content, subject_length)
        #self.outer['Subject'] = Header(subject, sys.getfilesystemencoding())
        self.outer['Subject'] = self.comment.doc_id + " " + self.comment.comment_id + " " + self.comment.date
        self.outer['To'] = config.email_admin
        self.outer['From'] = config.email_site
        self.outer['doc_id'] = self.comment.doc_id
        self.outer['comment_id'] = self.comment.comment_id
        self.outer['doc_date'] = self.comment.date
        data = MIMEText(self.comment.content)
        self.outer.attach(data)
        
    def _sendWithLocal(self):
        s = smtplib.SMTP('localhost')
        s.sendmail(config.email_site, config.email_admin, self.outer.as_string())
        s.quit()

    def _sendWithGmail(self):
        # We will meet SMTPAuthenticationError when invalid authenication.
        username = config.gmail_user
        password = config.gmail_password

        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(username, password)
        s.sendmail(config.email_site, config.email_admin, self.outer.as_string())
        s.quit()

    def _sendWithFile(self):
        pass

def sendMailUsingSendmail(obj):
    """

    >>> comment = Comment()
    >>> comment.doc_id = '1109012200'
    >>> comment.comment_id = '11'
    >>> comment.title = 'ttitle'
    >>> comment.date = '32'
    >>> comment.content = 'ccontent'
    >>> sendMailUsingSendmail(comment) #doctest: +SKIP
    """
    mailer = '/usr/sbin/sendmail'
    msg = \
        'To: '+ config.email_admin +\
        '\n' +\
        'From: '+ config.email_site +\
        '\n'+\
        'Subject: '+ 'Comment from ppf ' + obj.doc_id +\
        '\n'+\
        'doc_id: '+ obj.doc_id +\
        '\n'+\
        'comment_id: ' + obj.comment_id +\
        '\n'+\
        'doc_date: '+ obj.date +\
        '\n\n'+\
        obj.content
    p = os.popen('%s -t' % mailer, 'w')
    p.write(msg)
    p.close()


def sendMailUsingWebdotpy(obj):
    from_address = config.email_site
    to_address = config.email_admin
    subject = obj.title
    message = obj.content
    doc_id = obj.doc_id
    sendmail(from_address, to_address, subject, message, {'doc_id': doc_id})


def main():
    
    form = cgi.FieldStorage()
    
    if form.has_key('content') and form.has_key('doc_id'):
        doc_id = form['doc_id'].value
        addComment(doc_id, form)    
    else:
        try:
            doc_id = form['doc_id'].value
        except:
            print "Content-type: text/html\n"
            print hm.redirect_error
            exit(0)
        print "Content-type: text/html\n"
        print hm.redirect_requirement % doc_id

if __name__ == "__main__":
    main()
