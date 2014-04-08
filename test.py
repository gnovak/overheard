import unittest, re, tempfile, os

import arxiv_id, scrape, util, update, fetch, overheard

network_tests = True

# Actually want two of these, one old, one new.
test_aids = ['1401.0059', 'astro-ph/9909321']
test_delay = 5
test_file = "overheard.py"

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

# Old-style id, cases I want to be sure are handled.
#astro-ph0701006.pdf: PDF document, version 1.5
#astro-ph0701001.gz:  gzip compressed data, was "0701001.tar", from Unix, last modified: Fri Jan 19 05:47:49 2007, max compression
#astro-ph0701019.gz:  gzip compressed data, was "paper.tex", from Unix, last modified: Sun Dec 31 21:01:20 2006, max compression
# New style, common cases
# 1211.0027.pdf: PDF document, version 1.5
# 1211.0038.gz:  gzip compressed data, was "1211.3016.tar", from Unix, last modified: Thu Nov 15 16:06:56 2012, max compression
# 1211.0004.gz:  gzip compressed data, was "razmyshl_11_20.tex", from Unix, last modified: Thu Nov 22 04:38:00 2012, max speed

class OverheardTest(unittest.TestCase):

    def setUp(self):
        self.fetch_verbose_setting = fetch.verbose
        fetch.verbose = False

    def tearDown(self):
        fetch.verbose = self.fetch_verbose_setting

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

    def test_ensure_dir_exists(self):
        #the_dir = os.path.join(tempfile.mkdtemp(), 'aaa', 'bbb', 'file.txt')
        the_dir = os.path.join(tempfile.mkdtemp(), 'aaa')
        fetch.ensure_dir_exists(the_dir)

    def test_arxiv_to_url(self):
        for aid in test_aids:
            fetch.arxiv_to_url(aid)

    def test_fetch_command(self):
        for aid in test_aids:
            fetch.fetch_command(aid)

    def test_decompress_command(self):
        fetch.decompress_command("fake.tar")
            
    def test_gunzip_command(self):
        fetch.gunzip_command("fake.gz")

    def test_latex_file_name(self):
        for aid in test_aids:
            fetch.latex_file_name(aid)

    def test_file_name_base(self):
        for aid in test_aids:
            fetch.file_name_base(aid)

    def test_tar_file_name(self):
        for aid in test_aids:
            fetch.tar_file_name(aid)

    def test_tar_file_name_base(self):
        for aid in test_aids:
            fetch.tar_file_name_base(aid)

    def test_file_type_string(self):        
        fetch.file_type_string(test_file)

    def test_is_uncompressed_tar_file(self):
        fetch.is_uncompressed_tar_file(test_file)

    def test_is_gzip_file(self):
        fetch.is_gzip_file(test_file)

    def test_is_pdf_file(self):
        fetch.is_pdf_file(test_file)

    def test_is_tex_file(self):
        fetch.is_tex_file(test_file)

    def test_is_other_file(self):
        fetch.is_other_file(test_file)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_all_latex(self):
        fetch.fetch_all_latex(test_aids, delay=test_delay)

    @unittest.skipIf(not network_tests, "Skipping network tests.")
    def test_fetch_latex(self):
        for aid in test_aids:
            fetch.fetch_latex(aid)

    def test_get_all_latex(self):
        fetch.get_all_latex(test_aids)

    def test_get_latex(self):
        for aid in test_aids:
            fetch.get_latex(aid)
    

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
    

class ArchivTest(unittest.TestCase):

    def test_arxiv_id_old(self):
        # good ids
        self.assertTrue(arxiv_id.old('astro-ph/1234567'))
        self.assertTrue(arxiv_id.old('astro-ph/1234567v1'))
        self.assertTrue(arxiv_id.old('astro-ph/1234567v12'))

        # too short
        self.assertFalse(arxiv_id.old('astro-ph/123456'))
        self.assertFalse(arxiv_id.old('astro-ph/1234567v'))

        # too long
        self.assertFalse(arxiv_id.old('astro-ph/12345678'))

        # wrong letter
        self.assertFalse(arxiv_id.old('astro-ph/1234567a1'))

        # junk at start
        self.assertFalse(arxiv_id.old('astro-ph/a1234567'))
        self.assertFalse(arxiv_id.old('astro-ph/a1234567v1'))
        self.assertFalse(arxiv_id.old('astro-ph/a1234567v12'))

        # junk at end
        self.assertFalse(arxiv_id.old('astro-ph/1234567a'))
        self.assertFalse(arxiv_id.old('astro-ph/1234567v1a'))
        self.assertFalse(arxiv_id.old('astro-ph/1234567v12a'))

        # two versions
        self.assertFalse(arxiv_id.old('astro-ph/1234567v1v2'))

        # No archive name
        self.assertFalse(arxiv_id.old('/1234567v1v2'))

        # No slash
        self.assertFalse(arxiv_id.old('astro-ph1234567v1v2'))

    def test_arxiv_old_id_parse(self):
        self.assertEqual(arxiv_id.archive('astro-ph/1234567v12'), 'astro-ph')
        self.assertEqual(arxiv_id.yymm('astro-ph/1234567v12'), '1234')
        self.assertEqual(arxiv_id.number('astro-ph/1234567v12'), '567')
        self.assertEqual(arxiv_id.version('astro-ph/1234567v12'), 'v12')
        self.assertEqual(arxiv_id.version('astro-ph/1234567'), '')

    def test_arxiv_new_id_parse(self):
        self.assertEqual(arxiv_id.archive('1234.5678v12'), '')
        self.assertEqual(arxiv_id.yymm('1234.5678v12'), '1234')
        self.assertEqual(arxiv_id.number('1234.5678v12'), '5678')
        self.assertEqual(arxiv_id.version('1234.5678v12'), 'v12')
        self.assertEqual(arxiv_id.version('1234.5678'), '')

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
        for aid in test_aids:
            scrape.long_comments(aid)

    def test_short_comments(self):
        for aid in test_aids:
            scrape.short_comments(aid)

    def test_write_output(self):
        tf_1 = tempfile.NamedTemporaryFile()
        tf_2 = tempfile.NamedTemporaryFile()

        scrape.write_output(test_aids, 
                            tf_1.name, tf_2.name)
        
    # def test_all_comments(self):
    # for aid in test_aids:
    #     scrape.all_comments(aid)

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
