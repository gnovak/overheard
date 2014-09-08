import os, re

import feedparser

import util, fetch, arxiv_id

def fetch_rss():
    """Get RSS feed from arxiv.org"""
    return feedparser.parse('http://arxiv.org/rss/astro-ph')

def parse_rss():
    """Get RSS feed and pull new arxiv ids from it."""
    feed = fetch_rss()
    result = [ arxiv_id.extract_aid(el['id']) 
               for el in feed['entries']]
    return result

