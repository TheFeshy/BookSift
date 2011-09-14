'''This is a collection of tools useful for testing and verification.  Nothing in here
   should be used outside of the test cases.'''

import random
import array
import unittest
from zipfile import ZipFile
import os.path
import time

from Fingerprint import Fingerprint
from Exceptions import *
from Book import Book

'''This class is used to make 'OCR-like' errors in text files, to make our testing more
   realistic.  It is sloppy test code; please don't use it for anything else.'''
class ErrorMaker:
    def __init__(self):
        random.seed(42) #Because we want consistency in our testing, use a fixed random seed
    '''Functions to introduce error into text; use IntroduceErrors to do so in a uniform way'''
    def __SingleLetter(self, text, location):
        counter = 0
        for c in text[location:]:
            if not ' ' == c:
                text[location + counter] = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                break
            else:
                counter = counter + 1
        return text
    def __SingleCharacter(self, text, location):
        text[location] = random.choice('~`!@#$%^&*(){}:<>?[];')
        return text
    def __MissingSpace(self, text, location):
        for c in text[location:]:
            if ' ' == c:
                text = text[:location-1] + text[location:]
                break
        return text
    def __GarbageString(self, text, location):
        length = random.randint(3,25)
        if len(text) > location + length:
            for i in range(length):
                text[location + i] = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return text
    def __MissingPage(self, text, location):
        length = random.randint(800,1600)
        if len(text) > location + length:
            text = text[:location] + text[location+length:]
        return text
    def __RepeatPage(self, text, location): #A repeat of the previous page
        length = random.randint(800,1600)
        if len(text) > location + length:
            text = text[:location+length] + text[location:]
        return text
    '''Functions to introduce errors in the whole book, rather than a certain location'''
    def __InsertPerPageJunk(self,text, junk): #put some junk, like a web address, on every page
        somejunk = array.array('c')
        somejunk.fromstring(junk)
        currentindex = random.randint(100,200)
        while len(text) > currentindex:
            if text[currentindex] == ' ':
                text = text[:currentindex+1] + somejunk[:] + text[currentindex:]
                currentindex = currentindex + random.randint(1000,1600) + len(somejunk)
            else:
                currentindex = currentindex + 1
        return text
        
    
    def RelativeErrors(self, single_letter=0, single_character=0, missing_space=0,garbage_string=0, missing_page=0,repeat_page=0):
        return [(self.__SingleLetter,single_letter),
                (self.__SingleCharacter,single_character),
                (self.__MissingSpace, missing_space),
                (self.__GarbageString, garbage_string),
                (self.__MissingPage, missing_page),
                (self.__RepeatPage, repeat_page)]
        
    '''Introduces OCR-like errors in a text.
       text is the text to introduce errors into
       error_rate is how often errors are introduced; approximately 1 error every error_rate bytes
       relative_frequency is a list containing a function that introduces an error at a given location
       and a relative rate at which this function should be called'''
    def IntroduceErrors(self, text, error_rate, relative_frequency, pagejunk=''):
        errors = len(text)/error_rate
        arraytext = array.array('c')
        arraytext.fromstring(text)
        totalrf = 0
        errortable = []
        for func in relative_frequency:
            errortable.append((func[0],totalrf,totalrf+func[1]))
            totalrf = totalrf + func[1]
        while errors and totalrf:
            location = random.randint(0,len(arraytext) -1)
            choice = random.randint(0,totalrf)
            for er in errortable:
                if er[1] <= choice and choice < er[2]:
                    arraytext = er[0](arraytext, location)
                    break;
            errors = errors - 1
        if pagejunk:
            arraytext = self.__InsertPerPageJunk(arraytext, pagejunk)
        return arraytext.tostring()

testbookdir = '../testbooks/'
        
def SetUpTestBooks():
    bookarchive = ZipFile(os.path.join(testbookdir,'testbooks.zip'))
    books = {}
    #we just need three texts to run our tests with
    if len(bookarchive.namelist()) > 2:
        for i,arname in enumerate(bookarchive.namelist()):
            mybook = bookarchive.open(arname)
            text = mybook.read()
            originalfilename = os.path.join(testbookdir, 'book{0}original.txt'.format(i))
            errorfilename = os.path.join(testbookdir, 'book{0}error.txt'.format(i))
            of = open(originalfilename, 'w')
            ef = open(errorfilename, 'w')
            of.write(text)
            e = ErrorMaker()
            pagejunk = None
            if i == 2:
                pagejunk = 'http://website.that.is/onevery/page'
            text = e.IntroduceErrors(text, 4000 - (i*1800), e.RelativeErrors(24,6,12,2,1,1), pagejunk)
            ef.write(text)
            books['book{0}o'.format(i)]= originalfilename
            books['book{0}e'.format(i)]= errorfilename
    else:
        raise TBD('Not enough test books found to run test; aborting')
    return books

def CleanUpTestBooks():
    allfiles = os.listdir(testbookdir)
    for file in allfiles:
        if '.txt' == os.path.splitext(file)[1].lower():
            os.remove(os.path.join(testbookdir, file))
        
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
            except (InvalidType, EmptyBook):
                pass
    @staticmethod
    def uselesshash(word):
        return 42
        
    def test_emptybook(self): #Empty books should fail to be fingerprinted
        self.assertRaises(EmptyBook, Fingerprint, self.books['emptybook']) 
    def test_numericbook(self): #Books that have no alphabetical characters should fail to be fingerprinted
        self.assertRaises(EmptyBook, Fingerprint, self.books['numericbook'])
    def test_differenthash(self): #Verify that trying to compare fingerprings with different hashes fails
        self.assertRaises(DifferentHashes, self.fingerprints['book1'].compare_with, Fingerprint(self.books['book1'], FingerprintTest.uselesshash))
    def test_compareidentical(self): #Verify that identical books are marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1'])[0],'M')
    def test_comparenomatch(self): #Verify that different books are *not* marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book2'])[0],'N')
    def test_comparefuzzymatch(self): #Verify that books with some errors are still marked as matches
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1errors'])[0],'M')
    def test_caseinsensitivity(self): #Verify that the case of words in the book does not matter.
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1upper'])[0],'M')
    def test_comparesuperset(self): #Verify that we can identify if a book is a superset of another book
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1partial'])[0],'P')
    def test_comparesubset(self): #Verify that we can identify if a book is a subset of another book
        self.assertEqual(self.fingerprints['book1partial'].compare_with(self.fingerprints['book1'])[0],'B')
    def test_comparefuzzysuperset(self): #Verify that we can identify if a book is a superset of another book, even with errors
        self.assertEqual(self.fingerprints['book1'].compare_with(self.fingerprints['book1partialerrors'])[0],'P')
    def test_comparefuzzysubset(self): #Verify that we can identify if a book is a subset of another book, even with errors
        self.assertEqual(self.fingerprints['book1partialerrors'].compare_with(self.fingerprints['book1'])[0],'B')
    def test_unsupportedcomparison(self): #Verify that we fail on attempting to use a non-existent comparison type
        self.assertRaises(InvalidType, self.fingerprints['book1'].compare_with, Fingerprint(self.books['book1']), 'not a coparison method')
 
class BookTestShort(unittest.TestCase):
    def test_failstoreadnonexistantfile(self): #make sure we raise the proper exception if a file doesn't exist or can't be read
        book = Book(textfile='invalidfile.txt')
        self.assertRaises(CantGetText, book.initialize_text_data,hash)
        
class BookTest(unittest.TestCase):
    def setUp(self):
        self.books = {}
        self.booknames = SetUpTestBooks()
        for bookname,bookpath in self.booknames.iteritems():
            self.books[bookname]=Book(textfile=bookpath)
            self.books[bookname].initialize_text_data()
    def tearDown(self):
        CleanUpTestBooks()
    def test_identicalbooks(self): #Verify we match identical books
        result = self.books['book0o'].compare_with(self.books['book0o'])
        self.assertEqual(result[0],'M')
    def test_mismatchedbooks(self): #Verify we don't match different books
        result = self.books['book0o'].compare_with(self.books['book1o'])
        self.assertEqual(result[0],'N')
    def test_smallerrorbooks(self): #Verify we can match books with small errors
        result = self.books['book0o'].compare_with(self.books['book0e'])
        self.assertEqual(result[0],'M')
    def test_largeerrorbooks(self): #Verify we can match books even with many errors
        result = self.books['book2o'].compare_with(self.books['book2e'])
        self.assertEqual(result[0],'M')
    def test_quicknomatch(self):#make certain books that aren't even close miss quickly
        curtime = time.time()
        self.books['book0o'].compare_with(self.books['book1e'])
        runtime = time.time() - curtime
        self.assertTrue(runtime < 1.0)
    def test_quickrematch(self):#Verify that books that have already been checked are checked quickly
        self.books['book0o'].compare_with(self.books['book1e'])
        curtime = time.time()
        self.books['book0o'].compare_with(self.books['book1e'])
        runtime = time.time() - curtime
        self.assertTrue(runtime < 1.0)
                

def runTests():
    shorttests = (FingerprintTest, BookTestShort)
    
    longtests = (BookTest,)
    
    shortsuite = unittest.TestSuite()
    for test in shorttests:
        shortsuite.addTest(unittest.makeSuite(test, 'test'))
    runner = unittest.TextTestRunner()
    testresults = runner.run(shortsuite)
    if testresults.failures or testresults.errors:
        print 'Did not pass quick check; skipping longer checks'
        return False
    longsuite = unittest.TestSuite()
    for test in longtests:
        longsuite.addTest(unittest.makeSuite(test, 'test'))
    testresults = runner.run(longsuite)
    if testresults.failures or testresults.errors:
        return False
    return True

if __name__ == '__main__':
    
    runTests()
    
    
        
        