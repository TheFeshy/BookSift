'''Book is a collection of data associated with a Calibre book ID, and functions to
   act on that data.'''
 
from Fingerprint import Fingerprint
from Exceptions import TBD, CantGetText, NotInitialized 
import uuid
import Compare

class Book:
    '''Parameters:
       id is the calibre id, or 0 if not using calibre
       textfile is a path to the text file, if id is 0'''
    #TODO: impliment __getstate__ and __setstate__ for smaller pickling
    def __init__(self, calibreid=0, textfile=''):
        self.id = uuid.uuid4().int
        self.__textfilepath = None
        self.calibreid = calibreid
        
        self.__fingerprint = None
        
        self.__matches = {}
        self.__supersetof = {}
        self.__subsetof = {}
        
        self.__skip = False #True if we should skip this book due to error or user request
        self.__previous_completed_scans = set()
        self.statusmsg = 'Not examined'
        #if we are using this without calibre, or in test mode, use the text file parameter
        if not calibreid:
            self.__textfilepath = textfile
        else:
            TBD('Set skip status via calibre metadata')
    def get_relationships(self):
        return {'M':self.__matches, 'P':self.__supersetof, 'B':self.__subsetof}
    def __get_book_as_text(self):
        filename = None
        if self.__textfilepath:
            filename = self.__textfilepath
        else:
            raise TBD('Getting the text file from Calibre is not yet implimented')
        try:
            file = open(filename,'r')
            return file.read()
        except IOError as(errno, strerror):
            errtxt = 'Unable to open book as text; {0}:{1} (file:{2})'.format(errno,strerror,self.__textfilepath)
            self.statusmsg = errtxt
            self.__skip = True
            raise CantGetText(errtxt)
    '''Converts the book to text, and reads in the necessary data.
       Will raise a CantGetText if it can't get text.'''
    def get_textfilepath(self):
        return self.__textfilepath
    def complete_scan(self,scanid):
        self.__previous_completed_scans.add(scanid)
    def __was_previously_compared(self, book):
        for scanid in self.__previous_completed_scans:
            if scanid in book.__previous_completed_scans:
                return True
        return False
    def is_comparable(self):
        if self.__fingerprint and not self.__skip:
            return True
        else:
            return False
    def get_minhashes(self):
        if not self.__fingerprint:
            raise NotInitialized('Attempted to find minhashes on a book that has not been initialized')
        else:
            return self.__fingerprint.get_minhash()
    
    def initialize_text_data(self, hash_function=hash):
        if not self.__skip:
            if not self.__fingerprint:
                self.__fingerprint = Fingerprint(self.__get_book_as_text(), hash_function)
            else:
                pass #If we already have a fingerprint of the correct type, do nothing.
    '''Finds a fingerprint with a hashcheck in common with one of our local fingerprints (if it exists)'''
    def __match_fingerprints(self, book2):
        for fp1 in self.__fingerprintlist:
            for fp2 in book2.__fingerprintlist:
                if fp1.hashcheck == fp2.hashcheck:
                    return fp1, fp2
        else:
            raise NotInitialized('Attempted to compare books that have not been fingerprinted, or that do not have comparable fingerprints')
    def __get_existing_relationship(self, book2):
        if book2.id in self.__matches:
            return 'M',2
        elif book2.id in self.__subsetof:
            return 'B',2
        elif book2.id in self.__supersetof:
            return 'P',2
        else:
            return None
    def compare_with(self,book2):
        if self.__skip or book2.__skip:
            Compare.gPerfCounters.quickcompares += 1
            return ('N',2) #Books we ignore are effectively no match
        elif self.id == book2.id:
            Compare.gPerfCounters.quickcompares += 1
            return ('M',2) #technically, comparing a book with itself is a match...but don't add it to relationships; mathematicians asside "identity proofs" are not useful.
        preexisting = self.__get_existing_relationship(book2)
        if preexisting:
            Compare.gPerfCounters.quickcompares += 1
            return preexisting
        elif self.__was_previously_compared(book2):
            Compare.gPerfCounters.quickcompares += 1
            return ('N',2)
        if not self.__fingerprint and not book2.__fingerprint:
            raise NotInitialized('Attempted to compare books that have not been fingerprinted, or that do not have comparable fingerprints')
        result = self.__fingerprint.compare_with(book2.__fingerprint)
        if result[0] == 'M':
            self.__matches[book2.id]=result[1]
            book2.__matches[self.id]=result[1]
        elif result[0] == 'P':
            self.__supersetof[book2.id]=result[1]
            book2.__subsetof[self.id]=result[1]
        elif result[0] == 'B':
            self.__subsetof[book2.id]=result[1]
            book2.__supersetof[self.id]=result[1]
        elif result[0] == 'N':
            antiscore = 1 - result[1]
            if antiscore > Compare.gPerfCounters.highest_miss:
                Compare.gPerfCounters.highest_miss = antiscore
        return result

if __name__ == '__main__':
    import zUnitTest
    zUnitTest.run_testcase(zUnitTest.BookTest)
                
                
            
            