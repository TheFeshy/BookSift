
'''The Fingerprint class encapsulates a comparable fingerprint of a book that can be
   used to discover relationships to other books (using their fingerprints.)
'''


from __future__ import division #needed so that integer/integer = float
import re
from array import array

from Exceptions import EmptyBook, DifferentHashes

class Fingerprint:
    '''Takes the contents of a book (in text form) to initialize'''
    def __init__(self, book, hash_function=hash):
        #Get all unqiue words in the document
        self.__importantwords = self.__get_unique_words(book, hash_function)
        if not len(self.__importantwords):
            raise EmptyBook("Unable to locate alphabetical text to compare.")
        #Create a dictionary (which doubles as a 'set') of all the unique words,
        #and their index (the order they appear is important)
        self.__importantset = {}
        for i,c in enumerate(self.__importantwords):
            self.__importantset[c] = i
        self.__booklength = len(book)
        self.hashcheck = hash_function('magicvalue')
    
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
        size_ratio = min(self.__booklength,fp2.__booklength)/max(self.__booklength, fp2.__booklength)
        anthology = False
        minscore = self.__get_minscore_from_ratio(size_ratio)
        score = Fingerprint.__lcs_custom(self.__importantwords, self.__importantset, fp2.__importantwords, fp2.__importantset, minscore)
        if size_ratio < .8:
            anthology = True
        if minscore < score:
            #We have a book that matches, let's see what the relationship is:
            if not anthology:
                return 'M', score
            elif self.__booklength > fp2.__booklength:
                return 'P',score
            else:
                return 'B',score
        else:
            return 'N',1.0-score
    '''Creates an array consisting of the hashes of the unique words within the book'''
    @staticmethod
    def __get_unique_words(book, my_hash):
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
        for word in cleanbook:
            if isunique[word]:
                uniquewords.append(my_hash(word))
        #Array used to save space.  Array type is dependent on hash values though!
        #TODO: make this use the correct size on 32 bit systems
        return array('l',uniquewords)

    '''This function is based on a modified version of a longest common sequence search.
       Since all words are unique within a sequence, we can use a hash lookup instead of
       looping through to find matches.  Also, because we are interested in overall similarity
       more than just the "longest" match, we accumulate any match over a certain length and
       count it towards our score.
       
       meaningful_length is the number of consecutive characters to be considered a meaningful
       match
       quick_threshold is the percentage of words that must be present in both sets'''
    @staticmethod
    def __lcs_custom(seq1 ,set1, seq2, set2, quick_threshold, meaningful_length = 3):
        #Compare the shortest sequence to the longest hash for efficiency 
        if len(seq1) < len(seq2):
            shortseq = seq1
            longset = set2
        else:
            shortseq = seq2
            longset = set1
        totalscore = 0
        bestpossible = len(shortseq)
        nextexpected = 0 #The index of the next character, if the sequences match
        currentscore = 0
        miss = int(len(seq1) *(1-quick_threshold))
        for c1 in shortseq:
            c2 = longset.get(c1)
            if c2 == nextexpected:
                currentscore += 1
                nextexpected += 1
            else:
                miss -= 1
                if not miss:
                    return 0
                if currentscore > meaningful_length: #We no longer match, but remember how much we have matched so far
                    totalscore = totalscore + currentscore
                if c2: #If we at least found a character somewhere in the next sequence, start matching from there
                    nextexpected = c2 + 1
                    currentscore = 1
                else: #If we did not find our character somewhere, we can't start matching again yet.
                    nextexpected = 0
                    currentscore = 0
        else: #Don't forget whatever score remains at the end!
            if currentscore > meaningful_length:
                totalscore = totalscore + currentscore
        return totalscore / bestpossible