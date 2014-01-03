#!/usr/bin/python
# coding: utf-8

import collections
import os
import re

from sklearn.feature_extraction.text import CountVectorizer
from dlibs.logger import loggero
from dlibs.common import *

_current_abpath = os.path.abspath(__file__)
_current_path = os.path.dirname(_current_abpath)

def read_keywords(filename):
    path = os.path.join(_current_path, filename)
    fd = open(path, 'r')
    keywords = fd.read()
    return [u(ele) for ele in keywords.split('\n')]

_spam_words = read_keywords('data/spam_words')
_pos_words = read_keywords('data/pos_words')
_pos_spam_words = read_keywords('data/pos_spam_words')

class Var:
    tokenize_regexp = '\w+|\$[\d\.]+|(\[|\]|\)|\(|\/)|\S+'
    filter_regexp = "[\d\.,#+-]+|(\[|\]|\)|\(|\/)"
    spam_words = _spam_words
    pos_words = _pos_words

def is_spam(sentence):
    if word_counter(sentence, _pos_words, 2, 4):
        if word_counter(sentence, _pos_spam_words, 2, 4):
            return True
        return False
    if word_counter(sentence, _spam_words, 2, 4):
        return True
    return False

def is_near(text):
    regions = [u('부산'), u('창원'), u('마산'), u('경남'), u('울산')]
    if word_counter(text, regions, 2, 2):
        return True
    return False


def word_counter(content, words, min_n, max_n):
    """

    word have to be a lowercase.
    """
    keywords_d = {}
    for i in range(len(words)):
        keywords_d[words[i]] = i

    content = remove_special_chars(content)
    #loggero().debug(content)

    tokens = ngrams(content, min_n, max_n)
    vectorizer = CountVectorizer(min_df=1, vocabulary=keywords_d, ngram_range=(1, 1), lowercase=True)
    X = vectorizer.fit_transform(tokens).toarray()
    return X.sum()


def ngrams(tokens, MIN_N, MAX_N):
    n_tokens = len(tokens)
    for i in range(n_tokens):
        for j in range(i+MIN_N, min(n_tokens, i+MAX_N)+1):
            yield tokens[i:j]

def remove_special_chars(content):
    return re.sub("[^\w]", "", content, flags=re.UNICODE)


