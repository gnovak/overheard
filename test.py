import unittest

import arxiv_id, scrape

from overheard import *

# Run all tests from command line
#   python test.py
#   python -m test
#
# Run subset of tests from command line
#   python -m unittest ArchivTest
#   python -m unittest ArchivTest.test_old_arxiv_id
#   
# Run all tests non-interactively from REPL
#   import test; test.test()
#  
# Run specific test interactively from REPL
#   test.ArchivTest('test_old_arxiv_id').debug()
#

class ArchivTest(unittest.TestCase):

    def test_arxiv_id_old(self):
        # good ids
        self.assertTrue(arxiv_id.old('1234567'))
        self.assertTrue(arxiv_id.old('1234567v1'))
        self.assertTrue(arxiv_id.old('1234567v12'))

        # too short
        self.assertFalse(arxiv_id.old('123456'))
        self.assertFalse(arxiv_id.old('1234567v'))

        # too long
        self.assertFalse(arxiv_id.old('12345678'))

        # wrong letter
        self.assertFalse(arxiv_id.old('1234567a1'))

        # junk at start
        self.assertFalse(arxiv_id.old('a1234567'))
        self.assertFalse(arxiv_id.old('a1234567v1'))
        self.assertFalse(arxiv_id.old('a1234567v12'))

        # junk at end
        self.assertFalse(arxiv_id.old('1234567a'))
        self.assertFalse(arxiv_id.old('1234567v1a'))
        self.assertFalse(arxiv_id.old('1234567v12a'))

        # two versions
        self.assertFalse(arxiv_id.old('1234567v1v2'))

    def test_arxiv_id_new(self):
        # good ids
        self.assertTrue(arxiv_id.new('1234.5678'))
        self.assertTrue(arxiv_id.new('1234.5678v1'))
        self.assertTrue(arxiv_id.new('1234.5678v12'))

        # wrong delimiter
        self.assertTrue(arxiv_id.new('1234a5678'))

        # too short
        self.assertFalse(arxiv_id.new('123.5678'))
        self.assertFalse(arxiv_id.new('1234.567'))
        self.assertFalse(arxiv_id.new('1234.5678v'))

        # too long
        self.assertFalse(arxiv_id.new('1234.56788'))

        # wrong letter
        self.assertFalse(arxiv_id.new('1234.5678a1'))

        # junk at start
        self.assertFalse(arxiv_id.new('a1234.5678'))
        self.assertFalse(arxiv_id.new('a1234.5678v1'))
        self.assertFalse(arxiv_id.new('a1234.5678v12'))

        # junk at end
        self.assertFalse(arxiv_id.new('1234.5678a'))
        self.assertFalse(arxiv_id.new('1234.5678v1a'))
        self.assertFalse(arxiv_id.new('1234.5678v12a'))

        # two versions
        self.assertFalse(arxiv_id.new('1234.5678v1v2'))

class ScrapeTest(unittest.TestCase):

    def test_long_comment_regexp(self):
        self.assertTrue(re.search(scrape.long_comment_regexp, '% and comment'))
        self.assertTrue(re.search(scrape.long_comment_regexp, ' % and comment'))

        # make sure I get the whole comment
        self.assertEqual(re.search(scrape.long_comment_regexp, '%% and comment').group(1),
                         '%% and comment')
        self.assertEqual(re.search(scrape.long_comment_regexp, ' %% and comment').group(1),
                         '%% and comment')
        self.assertEqual(re.search(scrape.long_comment_regexp, '% and % comment').group(1),
                         '% and % comment')
        self.assertEqual(re.search(scrape.long_comment_regexp, ' % and % comment').group(1),
                         '% and % comment')

        # these are short comments
        self.assertFalse(re.search(scrape.long_comment_regexp, 'some text % and comment'))
        self.assertFalse(re.search(scrape.long_comment_regexp, 'some text %% and comment'))
        self.assertFalse(re.search(scrape.long_comment_regexp, 'some text % and % comment'))

    def test_short_comment_regexp(self):
        self.assertTrue(re.search(scrape.short_comment_regexp, 'some text % and comment'))

        # make sure I get the whole comment
        self.assertEqual(re.search(scrape.short_comment_regexp, 'some text % and % comment').group(1),
                         '% and % comment')
        self.assertEqual(re.search(scrape.short_comment_regexp, 'some text %% and comment').group(1),
                         '%% and comment')
                                
        # these are long comments
        #self.assertFalse(re.search(scrape.short_comment_regexp, '% and comment'))
        #self.assertFalse(re.search(scrape.short_comment_regexp, ' % and comment'))
        #self.assertFalse(re.search(scrape.short_comment_regexp, '%% and comment'))
        #self.assertFalse(re.search(scrape.short_comment_regexp, ' %% and commment'))
        #self.assertFalse(re.search(scrape.short_comment_regexp, '% and % comment'))
        #self.assertFalse(re.search(scrape.short_comment_regexp, ' % and % comment'))

def test():
    #suite = unittest.defaultTestLoader.loadTestsFromName('gsn_util.test')
    suite = unittest.defaultTestLoader.loadTestsFromName('test')
    unittest.TextTestRunner().run(suite)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    test()
