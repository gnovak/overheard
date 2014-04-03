def fetch_rss_maybe():
    """Get RSS feed.  Cache it to avoid hitting their server continuously
    while testing"""
    if False and os.path.exists('rss-feed.dat'):
        print "Using cached copy of rss feed"
        return uncan('rss-feed.dat')
    else:
        feed = feedparser.parse('http://arxiv.org/rss/astro-ph')
        can(feed, 'rss-feed.dat')
        return feed

def parse_rss_feed():
    feed = fetch_rss_maybe()
        
    result = [ re.search('.*/([0-9.v]*$)', entry['id']).group(1)
               for entry in feed['entries']]
    return result

