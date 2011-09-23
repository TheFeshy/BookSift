'''Unit test cases for every class

   There are several types of tests, denoted by a prefix on the function name:
   
   test_short_*  a test with this name should expect to complete in a fraction of a second
   test_medium_* a test with this name should complete within, at most, a few seconds
   test_long_*   a test with this name could take several seconds to complete
   test_big_*    for right now, our big "test 50 books" test'''

import unittest
import time
import threading

from Fingerprint import Fingerprint
from Exceptions import *
from Book import Book
import Library
import Utility
import Controller
import zTestDataManager
        
'''Test cases for the Fingerprint class'''
            
class FingerprintTest(unittest.TestCase):
    def setUp(self):
        self.books = { #Use these instead of our standard test books for a broader range of input    
        'book1':"It was a chilly November afternoon. I had just consummated an unusually hearty dinner, of which the dyspeptic truffe formed not the least important item, and was sitting alone in the dining-room, with my feet upon the fender, and at my elbow a small table which I had rolled up to the fire, and upon which were some apologies for dessert, with some miscellaneous bottles of wine, spirit and liqueur. In the morning I had been reading Glover's Leonidas, Wilkie's Epigoniad, Lamartine's Pilgrimage, Barlow's Columbiad, Tuckermann's Sicily, and Griswold's Curiosities ; I am willing to confess, therefore, that I now felt a little stupid. I made effort to arouse myself by aid of frequent Lafitte, and, all failing, I betook myself to a stray newspaper in despair. Having carefully perused the column of houses to let, and the column of dogs lost, and then the two columns of wives and apprentices runaway, I attacked with great resolution the editorial matter, and, reading it from beginning to end without understanding a syllable, conceived the possibility of its being Chinese, and so re-read it from the end to the beginning, but with no more satisfactory result. I was about throwing away, in disgust",
        'book1upper':"It was a chilly November afternoon. I had just consummated an unusually hearty dinner, of which the dyspeptic truffe formed not the least important item, and was sitting alone in the dining-room, with my feet upon the fender, and at my elbow a small table which I had rolled up to the fire, and upon which were some apologies for dessert, with some miscellaneous bottles of wine, spirit and liqueur. In the morning I had been reading Glover's Leonidas, Wilkie's Epigoniad, Lamartine's Pilgrimage, Barlow's Columbiad, Tuckermann's Sicily, and Griswold's Curiosities ; I am willing to confess, therefore, that I now felt a little stupid. I made effort to arouse myself by aid of frequent Lafitte, and, all failing, I betook myself to a stray newspaper in despair. Having carefully perused the column of houses to let, and the column of dogs lost, and then the two columns of wives and apprentices runaway, I attacked with great resolution the editorial matter, and, reading it from beginning to end without understanding a syllable, conceived the possibility of its being Chinese, and so re-read it from the end to the beginning, but with no more satisfactory result. I was about throwing away, in disgust".upper(),
        'book1errors':"It was a chilty November afternoon. I had jst consummated an gjnoaiwer dinner, of which the dyspeptic truffe formed not the least important stem, and was ssstting alone in the dining-room, with my page nine thousand feet upon the fender, and at my elbow a small table which I had rolled up to the fIre, and opon which were some apologies for dessert, with some miscellaneous Bottles of tine, spirit and liqueur. In the morning I had been reading Glover's Leonidas, Wilkie's Epigoniad, Lamartines Pilgrimage, Barlow's Columbiad, Tuckermann's Sicily, and Griswold's Curiosities ; I am willing to confess, therefore, that I now felt a little stepid. I made effort to arouse myself by aid of frequent Lafitte, and, all failing, I betook myself to a strry newspaper in despair. Having carefully perused the column of hooses to let, and the column of lost, and then the two columns of wives and apprentices runaway, I attacked with great resolution the editorial matter, and, reading it from beginning to end without understanding a syllable, conceived the possibility of its being Chinese, and so re-read it from the end to the beginning, but with no more satisfactory result. I was about throwing away, in disgust",
        'book1partial':"It was a chilly November afternoon. I had just consummated an unusually hearty dinner, of which the dyspeptic truffe formed not the least important item, and was sitting alone in the dining-room, with my feet upon the fender, and at my elbow a small table which I had rolled up to the fire, and upon which were some apologies for dessert, with some miscellaneous bottles of wine, spirit and liqueur. In the morning I had been reading Glover's Leonidas, Wilkie's Epigoniad, Lamartine's Pilgrimage, Barlow's Columbiad, Tuckermann's Sicily, and Griswold's Curiosities ; I am willing to confess, therefore, that I now felt a little stupid.",
        'book1partialerrors':"It was a chilty November afternoon. I had just consummated  hearty dinner, of which the dyspeptic truffe formed not the least important item, aRd was sitting alone in the dining-room, with my feet upon the fender, and at my elbow a smasl table which I had rolled up to the fire, and upon which were some apologies page 900 for dessert, with some miscellaneous bottles of wine, spirit anddd liqueur. In the morning I had been reading Glover's Leonidas, Wilkie's Epigoniad, Lamartine's Filgrimage, Barlow's Columbiad, Tuckermann's Sicily, and Griswold's Curiosities ; I am willing to confess, therefore, that I now felt a little stupid.",
        'book2':"My baptismal name is Egaeus; that of my family I will not mention. Yet there are no towers in the land more time-honored than my gloomy, gray, hereditary halls. Our line has been called a race of visionaries; and in many striking particulars --in the character of the family mansion --in the frescos of the chief saloon --in the tapestries of the dormitories --in the chiselling of some buttresses in the armory --but more especially in the gallery of antique paintings --in the fashion of the library chamber --and, lastly, in the very peculiar nature of the library's contents, there is more than sufficient evidence to warrant the belief. The recollections of my earliest years are connected with that chamber, and with its volumes --of which latter I will say no more. Here died my mother. Herein was I born. But it is mere idleness to say that I had not lived before --that the soul has no previous existence. You deny it? --let us not argue the matter. Convinced myself, I seek not to convince. There is, however, a remembrance of aerial forms --of spiritual and meaning eyes --of sounds, musical yet sad --a remembrance which will not be excluded; a memory like a shadow, vague, variable, indefinite, unsteady; and like a shadow, too, in the impossibility of my getting rid of it while the sunlight of my reason shall exist.",
        'book2partial':"The recollections of my earliest years are connected with that chamber, and with its volumes --of which latter I will say no more. Here died my mother. Herein was I born. But it is mere idleness to say that I had not lived before --that the soul has no previous existence. You deny it? --let us not argue the matter. Convinced myself, I seek not to convince. There is, however, a remembrance of aerial forms --of spiritual and meaning eyes --of sounds, musical yet sad --a remembrance which will not be excluded; a memory like a shadow, vague, variable, indefinite, unsteady; and like a shadow, too, in the impossibility of my getting rid of it while the sunlight of my reason shall exist.",
        'book3':"We will say, then, that I am mad. I grant, at least, that there are two distinct conditions of my mental existence -- the condition of a lucid reason, not to be disputed, and belonging to the memory of events forming the first epoch of my life -- and a condition of shadow and doubt, appertaining to the present, and to the recollection of what constitutes the second great era of my being. Therefore, what I shall tell of the earlier period, believe; and to what I may relate of the later time, give only such credit as may seem due, or doubt it altogether, or, if doubt it ye cannot, then play unto its riddle the Oedipus.",
        'numericbook':"12987213498571984735 ^%$@$%&(){}?><",
        'emptybook':""
        }
        self.fingerprints = {}
        for name,book in self.books.iteritems():
            try:
                self.fingerprints[name]=Fingerprint(book)
            except EmptyBook:
                pass

    @staticmethod
    def uselesshash(word):
        return 42
        
    def test_short_emptybook(self): #Empty books should fail to be fingerprinted
        self.assertRaises(EmptyBook, Fingerprint, self.books['emptybook']) 
    def test_short_numericbook(self): #Books that have no alphabetical characters should fail to be fingerprinted
        self.assertRaises(EmptyBook, Fingerprint, self.books['numericbook'])
    def test_short_differenthash(self): #Verify that trying to compare fingerprings with different hashes fails
        self.assertRaises(DifferentHashes, self.fingerprints['book1'].compare_with, Fingerprint(self.books['book1'], FingerprintTest.uselesshash))
    def test_short_compareidentical(self): #Verify that identical books are marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1'])[0],'M')
    def test_short_comparenomatch(self): #Verify that different books are *not* marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book2'])[0],'N')
    def test_short_comparefuzzymatch(self): #Verify that books with some errors are still marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1errors'])[0],'M')
    def test_short_caseinsensitivity(self): #Verify that the case of words in the book does not matter.
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1upper'])[0],'M')
    def test_short_comparesuperset(self): #Verify that we can identify if a book is a superset of another book
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1partial'])[0],'P')
    def test_short_comparesubset(self): #Verify that we can identify if a book is a subset of another book
        self.assertEqual(self.fingerprints['book1partial'].compare_with(self.fingerprints['book1'])[0],'B')
    def test_short_comparefuzzysuperset(self): #Verify that we can identify if a book is a superset of another book, even with errors
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1partialerrors'])[0],'P')
    def test_short_comparefuzzysubset(self): #Verify that we can identify if a book is a subset of another book, even with errors
        self.assertEqual(self.fingerprints['book1partialerrors'].compare_with(self.fingerprints['book1'])[0],'B')
       
class BookTest(unittest.TestCase):
    def setUp(self):
        self.testdata = zTestDataManager.TestBookManager('samplebooks.zip','../testbooks/')
    def tearDown(self):
        #TODO: this
        pass
    def test_short_failstoreadnonexistantfile(self): #make sure we raise the proper exception if a file doesn't exist or can't be read
        book = Book(textfile='invalidfile.txt')
        self.assertRaises(CantGetText, book.initialize_text_data,hash)
    def test_short_failstocompareunitializedbooks(self):
        book1 = Book(textfile='notused.txt')
        book2 = Book(textfile='alsonotused.txt')
        self.assertRaises(NotInitialized, book1.compare_with, book2)
    def test_medium_identical_books(self):
        self.testdata.unpack_archive(1)
        self.testdata.make_duplicate(number=1)
        library = Library.Library()
        Controller.process_books(library, book_text_files=self.testdata.get_testbooks())
        verification = self.testdata.verify_results(library)
        self.assertAlmostEqual(1.0, zTestDataManager.TestBookManager.combine_results(verification),3)
        
    def test_medium_mismatched_books(self):
        self.testdata.unpack_archive(2)
        library = Library.Library()
        Controller.process_books(library, book_text_files=self.testdata.get_testbooks())
        verification = self.testdata.verify_results(library)
        self.assertAlmostEqual(1.0, zTestDataManager.TestBookManager.combine_results(verification),3)
        
    def test_medium_small_error_compare(self):
        self.testdata.unpack_archive(1)
        e = zTestDataManager.ErrorMaker(error_rate=1600)
        self.testdata.make_error_dupes(number=1,errormaker=e)
        library = Library.Library()
        Controller.process_books(library, book_text_files=self.testdata.get_testbooks())
        verification = self.testdata.verify_results(library)
        self.assertAlmostEqual(1.0, zTestDataManager.TestBookManager.combine_results(verification),3)
        
    def test_medium_big_error_compare(self):
        self.testdata.unpack_archive(1)
        e = zTestDataManager.ErrorMaker(error_rate=500, per_page_junk=True)
        self.testdata.make_error_dupes(number=1,errormaker=e)
        library = Library.Library()
        Controller.process_books(library, book_text_files=self.testdata.get_testbooks())
        verification = self.testdata.verify_results(library)
        self.assertAlmostEqual(1.0, zTestDataManager.TestBookManager.combine_results(verification),3)
'''
    def test_quicknomatch(self):#make certain books that aren't even close miss quickly
        curtime = time.time()
        self.books['book0o'].compare_with(self.books['book1e'])
        runtime = time.time() - curtime
        self.assertTrue(runtime < 0.3)
    def test_quickrematch(self):#Verify that books that have already been checked are checked quickly
        self.books['book0o'].compare_with(self.books['book1e'])
        curtime = time.time()
        self.books['book0o'].compare_with(self.books['book1e'])
        runtime = time.time() - curtime
        self.assertTrue(runtime < 0.3)
    def test_matchpickledbook(self): #Verify that books work normally after being pickled
        tmp = tempfile.TemporaryFile()
        pickle.dump(self.books['book0o'],tmp,-1)
        pickle.dump(self.books['book0e'],tmp,-1)
        tmp.seek(0)
        pbook0 = pickle.load(tmp)
        pbook1 = pickle.load(tmp)
        result = pbook0.compare_with(pbook1)
        self.assertEqual(result[0],'M')
    def test_failpickledbook(self): #Verify that books work normally after being pickled
        tmp = tempfile.TemporaryFile()
        pickle.dump(self.books['book0o'],tmp,-1)
        pickle.dump(self.books['book1e'],tmp,-1)
        tmp.seek(0)
        pbook0 = pickle.load(tmp)
        pbook1 = pickle.load(tmp)
        result = pbook0.compare_with(pbook1)
        self.assertEqual(result[0],'N')
    def test_previouslycomparedbooksarenotrecompared(self):
        self.books['book0o'].complete_scan(42)
        self.books['book0e'].complete_scan(42)
        curtime = time.time()
        result = self.books['book0o'].compare_with(self.books['book0e'])
        runtime = time.time() - curtime
        self.assertEqual(result[0],'N') #Even though these match, this should return 'N' because we have declared that they have already been compared on a previous run
        self.assertTrue(runtime < 0.1) #Additionally; verify that this "already checked" result happens quickly!
'''
def slowarray(array, l, sleep):
    for i,c in enumerate(array[0]):
        with l:
            array[0][i] = i
        time.sleep(sleep)
            
def testfunc(n1, n2, result, bogus):
    retval = 'C'
    lock = result[0][1]
    with lock:
        if n1 < 0 or n2 < 0:
            retval = 'S'
        else:
            result[0][0][0] = result[0][0][0] + n1 + n2
    return retval
        
class UtilityTest(unittest.TestCase):
    def test_short_starved_compare_quick(self): #Verify that the "compare_all_despite_starvation" method works identical to a simple double loop
        testarray = [x for x in range(12)]
        total = 0 #We will test that all pairs are summed by getting the total of all pair additions
        paircount = 0
        for i, n1 in enumerate(testarray):
            for j, n2 in enumerate(testarray):
                if i < j:
                    paircount = paircount +1
                    total = total + n1 + n2
        testarray2 = [-1 for unused in range(12)]
        l = threading.Lock()
        t = threading.Thread(target=slowarray, args=((testarray2,),l,0))
        t.start()
        result = [0,]
        Utility.compare_all_despite_starvation(testarray2, len(testarray2), testfunc, 0, (result,l))
        self.assertEqual(total, result.pop())
    def test_long_slowlygeneratedarray(self): #Verify that the "compare_all_despite_starvation" works even when being forced to wait
        testarray = [x for x in range(50)]
        total = 0 #We will test that all pairs are summed by getting the total of all pair additions
        paircount = 0
        for i, n1 in enumerate(testarray):
            for j, n2 in enumerate(testarray):
                if i < j:
                    paircount = paircount +1
                    total = total + n1 + n2
        testarray2 = [-1 for unused in range(50)]
        l = threading.Lock()
        t = threading.Thread(target=slowarray, args=((testarray2,),l,0.04))
        t.start()
        result = [0,]
        Utility.compare_all_despite_starvation(testarray2, len(testarray2), testfunc, 0.02, (result,l))
        self.assertEqual(total, result.pop())
        
class LibraryTest(unittest.TestCase):
    def test_short_storeretrievebookbyuuid(self): #Verify the library can add and get books
        book = Book(textfile='invalidfile.txt')
        library = Library.Library()
        library.add_book(book)
        testvalue = False
        if library.get_book_uid(book.id):
            testvalue = True
        self.assertTrue(testvalue)
    def test_short_storeretrievebookbycalibreid(self): #Verify the library can add and get books by calibre id
        book = Book(calibreid=100)
        library = Library.Library()
        library.add_book(book)
        testvalue = False
        if library.get_book_cid(book.calibreid):
            testvalue = True
        self.assertTrue(testvalue)
    def test_short_failstofindnonexistantbookbyid(self):#Verfy we aren't finding ghost books
        book = Book(calibreid=100)
        library = Library.Library()
        library.add_book(book)
        testvalue = False
        if library.get_book_cid(101):
            testvalue = True
        self.assertFalse(testvalue)
    def test_short_deletingbook(self): #make sure delete actually removes books from the library
        book = Book(textfile='invalidfile.txt')
        library = Library.Library()
        library.add_book(book)
        testvalue = False
        if library.get_book_uid(book.id):
            testvalue = True
        self.assertTrue(testvalue)
        library.delete_book_uid(book.id)
        testvalue = False
        if library.get_book_uid(book.id):
            testvalue = True
        self.assertFalse(testvalue)
    def test_short_updatbook(self): #make certain that the library updates books properly
        book = Book(textfile='invalidfile.txt')
        library = Library.Library()
        book.statusmsg = False
        library.add_book(book)
        self.assertFalse(library.get_book_uid(book.id).statusmsg)
        book.statusmsg = True
        self.assertTrue(library.get_book_uid(book.id).statusmsg)

class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.testdata = zTestDataManager.TestBookManager('samplebooks.zip','../testbooks/')
        self.testdata.make_testcase(original_number=3, final_number=6)
    def test_long_basictest(self): #Just run through some books to be sure we don't crash
        library = Library.Library()
        Controller.process_books(library, book_text_files=self.testdata.get_testbooks())
        self.assertTrue(library.get_book_count() > 0) 
    def profilethis(self):
        print 'Test case generated. Beginning book matching'
        self.library = Library.Library()
        start = time.time()
        Controller.process_books(self.library, book_text_files=self.testdata.get_testbooks())
        runtime = time.time()-start
        #print library.print_pretty_tree()
        print 'Finished Processing {0} books in {1} seconds'.format(len(self.testdata.get_testbooks()),runtime)
    def test_big_compelete(self):
        print 'Setting up book test archive (this might take some time)'
        self.testdata = zTestDataManager.TestBookManager('samplebooks.zip','../testbooks/')
        self.testdata.make_testcase(final_number=50)
        import cProfile
        cProfile.runctx('self.profilethis()', globals(), locals(), 'profiledata')
        verification = self.testdata.verify_results(self.library)
        self.testdata.print_formatted_results(verification)
        print 'Total Score: {0:.1%}'.format(zTestDataManager.TestBookManager.combine_results(verification))
        self.assertTrue(True) 

def build_test_suites():
    myTestSuites = {}
    test_cases = [FingerprintTest, BookTest, LibraryTest, UtilityTest,ControllerTest]
    test_types = ['short', 'medium', 'long', 'big']
    for type in test_types:
        suite = unittest.TestSuite()
        for case in test_cases:
            suite.addTest(unittest.makeSuite(case, 'test_{0}'.format(type)))
        myTestSuites[type] = suite
    return myTestSuites

def run_testcase(case):
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(case, 'test'))
    runner.run(suite)

def run_suite(suite, name = '', skipif=False):
    if skipif:
        print "Failed previous tests, skipping {0}".format(name)
    else:
        runner = unittest.TextTestRunner()
        print "Running suite {0}".format(name)
        testresults = runner.run(suite)
        if testresults.failures or testresults.errors:
            return False
        else:
            return True        

if __name__ == '__main__':
    
    skipif = False
    global myTestSuites
    suites = build_test_suites()
    print "Running all available tests"
    for name, suite in suites.iteritems():
        skipif = not run_suite(suite, name, skipif) 
    
    
        
        