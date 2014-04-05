import unittest, re, tempfile, os

import arxiv_id, scrape, util, update, fetch, overheard

network_tests = True

test_aid = '1401.0059'
test_delay = 5

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

class OverheardTest(unittest.TestCase):

    def setUp(self):
        self.fetch_verbose_setting = fetch.verbose
        self.update_verbose_setting = update.verbose
        fetch.verbose = False
        update.verbose = False

    def tearDown(self):
        fetch.verbose = self.fetch_verbose_setting
        update.verbose = self.update_verbose_setting

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_main(self):
        overheard.main(delay=test_delay, prefix=tempfile.gettempdir(), nmax=2)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_download_todays_papers(self):
        overheard.download_todays_papers(delay=test_delay, nmax=2)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def do_it_all(self):
        tf_1 = tempfile.NamedTemporaryFile()
        tf_2 = tempfile.NamedTemporaryFile()
        overheard.do_it_all(tf_1.name, tf_2.name, delay=test_delay, nmax=2)

class FetchTest(unittest.TestCase):
    def setUp(self):
        self.verbose_setting = fetch.verbose
        fetch.verbose = False

    def tearDown(self):
        fetch.verbose = self.verbose_setting

    def test_extension(self):
        fetch.extension('filename.txt')

    def test_arxiv_to_url(self):
        fetch.arxiv_to_url(test_aid)

    def test_fetch_command(self):
        fetch.fetch_command(test_aid)

    def test_decompress_command(self):
        fetch.decompress_command(test_aid)

    def test_gunzip_command(self):
        fetch.gunzip_command(test_aid)

    # FIXME -- this is set to run in particular dir
    # def test_gunzip(self):
    #     fetch.gunzip(test_aid)

    def test_latex_file_name(self):
        fetch.latex_file_name(test_aid)

    def test_tar_file_name(self):
        fetch.tar_file_name(test_aid)

    def test_file_type_string(self):
        fetch.file_type_string(test_aid)

    def test_is_uncompressed_tar_file(self):
        fetch.is_uncompressed_tar_file(test_aid)

    def test_is_gzipped_tar_file(self):
        fetch.is_gzipped_tar_file(test_aid)

    def test_is_gzipped_tex_file(self):
        fetch.is_gzipped_tex_file(test_aid)

    def test_is_pdf(self):
        fetch.is_pdf(test_aid)

    def test_is_valid_latex(self):
        fetch.is_valid_latex(test_aid)

    def is_valid_latex(self):
        fetch.is_valid_latex(test_aid)

    def test_is_valid_non_latex(self):
        fetch.is_valid_non_latex(test_aid)

    def test_is_unknown(self):    
        fetch.is_unknown(test_aid)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_all_latex(self):
        fetch.fetch_all_latex([test_aid], delay=test_delay)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_latex(self):
        fetch.fetch_latex(test_aid)

    def test_get_all_latex(self):
        fetch.get_all_latex([test_aid, test_aid])

    def test_get_latex(self):
        fetch.get_latex(test_aid)
    

class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.verbose_setting = update.verbose
        update.verbose = False

    def tearDown(self):
        update.verbose = self.verbose_setting

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_rss_maybe(self): 
        update.fetch_rss_maybe()
    
    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_parse_rss_feed_maybe(self): 
        update.parse_rss_feed()

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

    # Note that latex file for test_aid must exist

    def test_long_comments(self):
        scrape.long_comments(test_aid)

    def test_short_comments(self):
        scrape.short_comments(test_aid)

    def test_write_output(self):
        tf_1 = tempfile.NamedTemporaryFile()
        tf_2 = tempfile.NamedTemporaryFile()

        scrape.write_output([test_aid, test_aid], 
                            tf_1.name, tf_2.name)
        
    # def test_all_comments(self):
    #     scrape.all_comments(test_aid)

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
