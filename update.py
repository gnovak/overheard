import os, re

import feedparser

import util

def fetch_rss():
    """Get RSS feed from arxiv.org"""
    return feedparser.parse('http://arxiv.org/rss/astro-ph')

def parse_rss():
    """Get RSS feed and pull new arxiv ids from it."""
    feed = fetch_rss()        
    result = [ re.search('.*/([0-9.v]*$)', entry['id']).group(1)
               for entry in feed['entries']]
    return result

