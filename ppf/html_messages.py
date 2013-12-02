#!/usr/bin/python
# coding: utf-8

redirect = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Posting</title>
<meta http-equiv="REFRESH" content="0;url=/article/%s"></HEAD>
<BODY>
Posting...
</BODY>
</HTML>"""

redirect_requirement = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Error</title>
<meta http-equiv="REFRESH" content="2;url=/article/%s"></HEAD>
<BODY>
최소한 내용은 적어 주세요.
</BODY>
</HTML>"""

redirect_error = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Error</title>
<meta http-equiv="REFRESH" content="2;url=/"></HEAD>
<BODY>
잘못된 접근입니다.
</BODY>
</HTML>"""

redirect_wait_updating = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Error</title>
</HEAD>
<BODY>
공사중입니다. 잠시후에 접속해 주세요. 한 10초???
</BODY>
</HTML>"""

redirect_error_limit_comments = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Posting</title>
<meta http-equiv="REFRESH" content="10;url=/article/%s"></HEAD>
<BODY>
We can not write the comment, <br>
because this article has <b>limited the count</b> for posting comments.<br>
This page will automatically redirected to the previous page.
</BODY>
</HTML>"""


def redirect_doc(title, wait_time, doc_id, body):
    result = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>%s</title>
<meta http-equiv="REFRESH" content="%s;url=/article/%s"></HEAD>
<BODY>
%s
</BODY>
</HTML>""" % (title, wait_time, doc_id, body)
    print "Content-type: text/html\n"
    print result

def print_msg(msg):
    print "Content-type: text/html\n"
    print msg
