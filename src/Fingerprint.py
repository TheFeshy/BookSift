
'''The Fingerprint class encapsulates a comparable fingerprint of a book that can be
   used to discover relationships to other books (using their fingerprints.)
'''


from __future__ import division #needed so that integer/integer = float
import re
from array import array

from Exceptions import EmptyBook, DifferentHashes, NotInitialized
import Compare
import Cfg
if Cfg.myOptions.useC:
    import OptimizeCompare
import Utility
import operator

class Fingerprint:
    '''Takes the contents of a book (in text form) to initialize'''
    def __init__(self, book, hash_function=hash):
        self.__minhashes = None
        #Get all unique words in the document
        self.__importantwords = self.__get_unique_words(book, hash_function)
        if not len(self.__importantwords):
            raise EmptyBook("Unable to locate alphabetical text to compare.")
        #Create a dictionary (which doubles as a 'set') of all the unique words,
        #and their index (the order they appear is important)
        if Cfg.myOptions.useC:
            self.__importantset = OptimizeCompare.HashLookupTable()
        else:
            self.__importantset = {}
        for i,c in enumerate(self.__importantwords):
            self.__importantset[c] = i
        self.__booklength = len(book)
        self.hashcheck = hash_function('magicvalue')
    def get_minhash(self):
        if not self.__minhashes:
            raise NotInitialized('Attempting to compare fingerprints from an uninitialized book')
        else:
            return self.__minhashes
    
    '''This function has the look of one pulled out of thin air... it pretty much was. '''  
    def __get_minscore_from_ratio(self, ratio):
        return  min(.7,max(-.4/ratio +.85,.15))
    '''Determines the relationship with another Fingerprint, using optional thresholds
       parameters:
       method determins the method used.  the default is 'dl' for a Damerau-Levenshtein comparison
       quick_threshold determines the percentage of unique words that must be present for further comparison
       long_threshold determines the percentage of the unique words in a book that do not need to be changed in order to indicate a match
       match_threshold determines how close in length the books can be to be considered a match
       Returns:
       a tupple with the relationship, and confidence:
       'N' for No relationship
       'B' if this book is a suBset of the second book
       'P' if this book is a suPerset of the second book
       'M' if this book is a Match of the second book
       exceptions:
       Can throw DifferentHashes if the fingerprints were hashed using incompatible hashes.'''
    def compare_with(self,fp2):
        if not self.hashcheck == fp2.hashcheck:
            raise DifferentHashes('Attempted to compare two fingerprints that have been created using different hashes')
        size1 = self.__booklength
        size2 = fp2.__booklength
        seqsize1 = len(self.__importantwords)
        seqsize2 = len(fp2.__importantwords)
        score = -1
        method = 0
        for compare in Compare.gCompareParams:
            allowed_consecutive_error = compare.allowed_consecutive_errors(size1, size2, seqsize1, seqsize2)
            allowed_distance_error = compare.allowed_displacement_error(size1, size2, seqsize1, seqsize2)
            meaningful_length = compare.meaningful_length(size1, size2, seqsize1, seqsize2, allowed_consecutive_error)
            min_score = compare.min_score(size1, size2, seqsize1, seqsize2)
            count_misses = compare.count_misses
            score = compare.search_method(self.__importantwords, self.__importantset, fp2.__importantwords, fp2.__importantset, min_score, meaningful_length, allowed_consecutive_error, allowed_distance_error, count_misses)
            slow_cutoff = compare.slow_cutoff(size1, size2,seqsize1, seqsize2)
            user_score = compare.adjust_score(score, size1, size2, seqsize1, seqsize2)
            if score < min_score or score > slow_cutoff:
                break
            else:
                Compare.gPerfCounters.fallback_compare[method] += 1
        else:
            if score < 0:
                raise NotInitialized('No search types were ever created; no search was done.')
        if min_score < score:
            Compare.gPerfCounters.hits += 1
            #We have a book that matches, let's see what the relationship is:
            if (min(size1,size2)/max(size1,size2)) > 0.9:
                return 'M', user_score
            elif self.__booklength > fp2.__booklength:
                return 'P',user_score
            else:
                return 'B',user_score
        else:
            Compare.gPerfCounters.misses += 1
            return 'N',1.0-user_score
    '''Creates an array consisting of the hashes of the unique words within the book'''
    def __get_unique_words(self, book, my_hash):
        isunique = {}
        uniquewords = []
        #Create a case-insensitive list, removing all numbers and punctuation
        cleanbook = re.sub('[\W\d_]+',' ',book.lower()).split()
        #create a dictionary to identify unique words
        for word in cleanbook:
            if word in isunique:
                isunique[word]=False
            else:
                isunique[word]=True
        #Next, make an in-order list of the hash of the unique words
        #for word, unique in isunique.iteritems():
        for word in cleanbook:
            if isunique[word]:
                uniquewords.append(my_hash(word))
        self.__minhashes = self.__generate_minhashes(cleanbook)
        #Array used to save space.  Array type is dependent on hash values though!
        #TODO: make this use the correct size on 32 bit systems
        if Cfg.myOptions.useC:
            return OptimizeCompare.HashSequence(uniquewords)
        else:
            return array('l', uniquewords)
        
    def __shingle_and_hash(self, words, shingle_size, L_tables):
        if not Cfg.myOptions.useC:
            minhashes = array('l', (9223372036854775807 for n in xrange(L_tables)))
            for i in xrange(len(words) - shingle_size):
                shingle = tuple(words[i:i+shingle_size])
                hshingle = hash(shingle)
                #I've tried all manner of map() to remove this inner loop; but no luck.
                #Python's poor "for" statement and super slow xor means this takes over a second per book.
                for h in xrange(L_tables-1):
                    myhash = hshingle ^ Utility.myMasks.masks[h]
                    if myhash < minhashes[h]:
                        minhashes[h] = myhash
        else:
            hashedwords = len(words)
            hashes = OptimizeCompare.HashSequence()
            hashes.resize(hashedwords, 0)
            for i in xrange(hashedwords):
                hashes[i] = hash(words[i])
            myhashes = OptimizeCompare.HashSequence()
            myhashes = OptimizeCompare.shingle_and_hash(hashes, Utility.myMasks.masks, L_tables, shingle_size)
            minhashes = array('l',myhashes) #Convert to native python type because this array is small, but will be accessed frequently!
        return minhashes
                
            
    def __generate_minhashes(self,words, shingle_size=5):
        L_tables = Compare.myMinHashParams.minhash_tables
        if len(words) < 4:
            return array('l',[])
        elif len(words) < shingle_size:
            shingle_size = 1
        return self.__shingle_and_hash(words, shingle_size, L_tables)
        #self.__find_mins(tables, L_tables, minhashes)
                    
        
        
        
    
if __name__ == '__main__':
    import zUnitTest
    zUnitTest.run_testcase(zUnitTest.FingerprintTest)
    