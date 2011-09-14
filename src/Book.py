'''Book is a collection of data associated with a Calibre book ID, and functions to
   act on that data.'''
 
from Fingerprint import Fingerprint
from Exceptions import TBD, CantGetText, NotInitialized 
import uuid
   
class Book:
    '''Parameters:
       id is the calibre id, or 0 if not using calibre
       textfile is a path to the text file, if id is 0'''
    def __init__(self, calibreid=0, textfile=''):
        self.id = uuid.uuid1()
        self.__textfilepath = None
        self.__calibreid = calibreid
        
        self.__fingerprintlist = []
        
        self.__matches = set()
        self.__supersetof = set()
        self.__subsetof = set()
        
        self.__skip = False #True if we should skip this book due to error or user request
        self.statusmsg = 'Not examined'
        #if we are using this without calibre, or in test mode, use the text file parameter
        if not calibreid:
            self.__textfilepath = textfile
        #TODO: set skip status via calibre metadata
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
    '''Looks through fingerprints in our list to see if it has the correct fingerprint to use'''
    def __get_correct_fingerprint(self, method_hash):
        for fp in self.__fingerprintlist: #Linear search; we will usually have one, at most two or three
            if fp.hashcheck == method_hash:
                return fp
        return None #Otherwise, return nothing
    '''Converts the book to text, and reads in the necessary data.
       Will raise a CantGetText if it can't get text.'''
    def initialize_text_data(self, important_words = 'unique', hash_function=hash):
        if not self.__skip:
            hashcheck = Fingerprint.hashcheck_from_options(important_words, hash_function)
            if not self.__get_correct_fingerprint(hashcheck):
                self.__fingerprintlist.append(Fingerprint(self.__get_book_as_text(), important_words, hash_function))
            else:
                pass #If we already have a fingerprint of the correct type, do nothing.
            #TODO: create new quote list
    '''In case books support multiple fingerprints for testing, allow a "preferred" one to be set.'''
    def set_prefered_fingerprint(self, method_hash):
        for i,fp in enumerate(self.__fingerprintlist):
            if fp.hashcheck == method_hash and not i == 0: #If we find the hash somewhere other than the first slot, swap it:
                tmp = fp
                self.__fingerprintlist[i] = self.__fingerprintlist[0]
                self.__fingerprintlist[0] = tmp
            if self.__fingerprintlist[0].hashckech == method_hash:
                return True
        return False
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
            return 'M'
        elif book2.id in self.__subsetof:
            return 'B'
        elif book2.id in self.__supersetof:
            return 'P'
        else:
            return None
    def compare_with(self,book2):
        if self.__skip or book2.__skip:
            return 'N',100 #Books we ignore are effectively no match
        preexisting = self.__get_existing_relationship(book2)
        if preexisting:
            return preexisting
        fp1, fp2 = self.__match_fingerprints(book2)
        result = fp1.compare_with(fp2)
        if result[0] == 'M':
            self.__matches.add(book2.id)
            book2.__matches.add(self.id)
        elif result[0] == 'P':
            self.__supersetof.add(book2.id)
            book2.__subsetof.add(self.id)
        elif result[0] == 'B':
            self.__subsetof.add(book2.id)
            book2.__supersetof.add(self.id)
        return result

    
                
                
            
            