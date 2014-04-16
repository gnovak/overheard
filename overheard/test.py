#########
# Notes #
#########
# 
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
from __future__ import with_statement

import unittest, re, tempfile, os

if not hasattr(unittest, 'skipIf'):
    try: 
        import unittest2 as unittest        
    except ImportError:
        raise NotImplementedError, \
            """Tests require either the Python 2.7 or later version of the unittest module or
            the unittest2 module."""

import arxiv_id, scrape, util, update, fetch, overheard

network_tests = True

test_aids = ['astro-ph/0701019',    # gzipped tex file
             'astro-ph/0701528',    # gzipped tar file
             'astro-ph/0701864',    # PDF file
             '1211.1574',           # gzipped tex file
             '1211.4164',           # gzipped tar file
             '1211.2577']           # PDF file

test_delay = 2
test_file = "overheard.py"

class OverheardTest(unittest.TestCase):

    def setUp(self):
        self.fetch_verbose_setting = fetch.verbose
        self.scrape_verbose_setting = scrape.verbose
        fetch.verbose = False
        scrape.verbose = False

    def tearDown(self):
        fetch.verbose = self.fetch_verbose_setting
        scrape.verbose = self.scrape_verbose_setting

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_process_todays_papers(self):
        overheard.process_todays_papers(delay=test_delay, 
                                        prefix=tempfile.gettempdir(), nmax=2)


class FetchTest(unittest.TestCase):
    def setUp(self):
        self.verbose_setting = fetch.verbose
        fetch.verbose = False

    def tearDown(self):
        fetch.verbose = self.verbose_setting

    def test_extension(self):
        fetch.extension('filename.txt')

    def test_ensure_dirs_exist(self):
        the_dir = os.path.join(tempfile.mkdtemp(), 'aa', 'bb', 'file.txt')
        fetch.ensure_dirs_exist(the_dir)

    def test_arxiv_to_url(self):
        for aid in test_aids:
            fetch.arxiv_to_url(aid)

    def test_fetch_command(self):
        for aid in test_aids:
            fetch.fetch_command(aid, "filename")

    def test_untar_command(self):
        fetch.untar_command("fake.tar")
            
    def test_gunzip_command(self):
        fetch.gunzip_command("fake.gz")

    def test_latex_file_name(self):
        for aid in test_aids:
            fetch.latex_file_name(aid)

    def test_latex_file_path(self):
        for aid in test_aids:
            fetch.latex_file_path(aid)

    def test_file_name_base(self):
        for aid in test_aids:
            fetch.file_name_base(aid)

    def test_source_file_extension(self):
        for aid in test_aids:
            fetch.source_file_extension(aid)

    def test_source_file_exists(self):
        for aid in test_aids:
            fetch.source_file_exists(aid)

    def test_source_file_name(self):
        for aid in test_aids:
            fetch.source_file_name(aid)

    def test_source_file_path(self):
        for aid in test_aids:
            fetch.source_file_path(aid)

    def test_source_file_path_without_extension(self):
        for aid in test_aids:
            fetch.source_file_path_without_extension(aid)

    def test_file_type_string(self):        
        fetch.file_type_string(test_file)

    def test_is_tar(self):
        fetch.is_tar(test_file)

    def test_is_gzip(self):
        fetch.is_gzip(test_file)

    def test_is_pdf(self):
        fetch.is_pdf(test_file)

    def test_is_tex(self):
        fetch.is_tex(test_file)

    def test_is_other(self):
        fetch.is_other(test_file)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_source_and_latex(self):
        # the exercises fetch.source, fetch.all_source, fetch.latex, and
        # fetch.all_latex
        fetch.all_source(test_aids, delay=test_delay, force=True)
        fetch.all_latex(test_aids)
    

class UpdateTest(unittest.TestCase):

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_rss(self): 
        update.fetch_rss()
    
    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_parse_rss(self): 
        update.parse_rss()

class UtilTest(unittest.TestCase):
    def test_remember_cwd(self): 
        cwd = os.getcwd()
        with util.remember_cwd():
            os.chdir("..")
        self.assertEqual(os.getcwd(), cwd)
        
    def test_can_uncan_file_object(self):         
        obj = [1,2,3]
        tf = tempfile.TemporaryFile()
        util.can(obj, tf)
        tf.seek(0)
        self.assertEqual(util.uncan(tf), obj)

    def test_can_uncan_file_name(self): 
        obj = [1,2,3]
        tf = tempfile.NamedTemporaryFile()
        util.can(obj, tf.name)
        tf.seek(0)
        self.assertEqual(util.uncan(tf.name), obj)
    
class ArxivIdTest(unittest.TestCase):

    def test_old(self):
        # good ids
        self.assertTrue(arxiv_id.is_old('astro-ph/1234567'))
        self.assertTrue(arxiv_id.is_old('astro-ph/1234567v1'))
        self.assertTrue(arxiv_id.is_old('astro-ph/1234567v12'))

        # too short
        self.assertFalse(arxiv_id.is_old('astro-ph/123456'))
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567v'))

        # too long
        self.assertFalse(arxiv_id.is_old('astro-ph/12345678'))

        # wrong letter
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567a1'))

        # junk at start
        self.assertFalse(arxiv_id.is_old('astro-ph/a1234567'))
        self.assertFalse(arxiv_id.is_old('astro-ph/a1234567v1'))
        self.assertFalse(arxiv_id.is_old('astro-ph/a1234567v12'))

        # junk at end
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567a'))
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567v1a'))
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567v12a'))

        # two versions
        self.assertFalse(arxiv_id.is_old('astro-ph/1234567v1v2'))

        # No archive name
        self.assertFalse(arxiv_id.is_old('/1234567v1v2'))

        # No slash
        self.assertFalse(arxiv_id.is_old('astro-ph1234567v1v2'))

    def test_old_id_parse(self):
        self.assertEqual(arxiv_id.archive('astro-ph/1234567v12'), 'astro-ph')
        self.assertEqual(arxiv_id.yymm('astro-ph/1234567v12'), '1234')
        self.assertEqual(arxiv_id.number('astro-ph/1234567v12'), '567')
        self.assertEqual(arxiv_id.version('astro-ph/1234567v12'), 'v12')
        self.assertEqual(arxiv_id.version('astro-ph/1234567'), '')

    def test_new_id_parse(self):
        self.assertEqual(arxiv_id.archive('1234.5678v12'), '')
        self.assertEqual(arxiv_id.yymm('1234.5678v12'), '1234')
        self.assertEqual(arxiv_id.number('1234.5678v12'), '5678')
        self.assertEqual(arxiv_id.version('1234.5678v12'), 'v12')
        self.assertEqual(arxiv_id.version('1234.5678'), '')

    def test_is_new(self):
        # good ids
        self.assertTrue(arxiv_id.is_new('1234.5678'))
        self.assertTrue(arxiv_id.is_new('1234.5678v1'))
        self.assertTrue(arxiv_id.is_new('1234.5678v12'))

        # wrong delimiter
        self.assertTrue(arxiv_id.is_new('1234a5678'))

        # too short
        self.assertFalse(arxiv_id.is_new('123.5678'))
        self.assertFalse(arxiv_id.is_new('1234.567'))
        self.assertFalse(arxiv_id.is_new('1234.5678v'))

        # too long
        self.assertFalse(arxiv_id.is_new('1234.56788'))

        # wrong letter
        self.assertFalse(arxiv_id.is_new('1234.5678a1'))

        # junk at start
        self.assertFalse(arxiv_id.is_new('a1234.5678'))
        self.assertFalse(arxiv_id.is_new('a1234.5678v1'))
        self.assertFalse(arxiv_id.is_new('a1234.5678v12'))

        # junk at end
        self.assertFalse(arxiv_id.is_new('1234.5678a'))
        self.assertFalse(arxiv_id.is_new('1234.5678v1a'))
        self.assertFalse(arxiv_id.is_new('1234.5678v12a'))

        # two versions
        self.assertFalse(arxiv_id.is_new('1234.5678v1v2'))

class ScrapeTest(unittest.TestCase):

    def setUp(self):
        # Need the latex files for these tests to make sense.  They
        # may be fetched once, thereafter cached versions will be
        # used.
        #
        # This means that all of the tests in this class depend on the
        # network

        self.fetch_verbose_setting = fetch.verbose
        self.scrape_verbose_setting = scrape.verbose
        fetch.verbose = False
        scrape.verbose = False

        any_fetched = fetch.all_source(test_aids, delay=test_delay)
        if any_fetched: 
            fetch.all_latex(test_aids)

    def tearDown(self):
        fetch.verbose = self.fetch_verbose_setting
        scrape.verbose = self.scrape_verbose_setting

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_long_comments(self):
        for aid in test_aids:
            scrape.long_comments(aid)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_short_comments(self):
        for aid in test_aids:
            scrape.short_comments(aid)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_write_output(self):
        tf_1 = tempfile.NamedTemporaryFile()
        tf_2 = tempfile.NamedTemporaryFile()

        scrape.write_output(test_aids, 
                            tf_1.name, tf_2.name)
        
    # def test_all_comments(self):
    # for aid in test_aids:
    #     scrape.all_comments(aid)

class CommentRegexpTest(unittest.TestCase):
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
    suite = unittest.defaultTestLoader.loadTestsFromName('test')
    unittest.TextTestRunner().run(suite)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    test()
