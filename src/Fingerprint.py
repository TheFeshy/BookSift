
'''The Fingerprint class encapsulates a comparable fingerprint of a book that can be
   used to discover relationships to other books (using their fingerprints.)
'''


from __future__ import division #needed so that integer/integer = float
import re
from array import array

from Exceptions import InvalidType, EmptyBook, DifferentHashes
import utility

class Fingerprint:
    '''This class stores a hash value, and the index of the location which it originally appeared'''
    class UniqueWordPosition:
        def __init__(self, hash, index):
            self.hash = hash
            self.index = index
        def __eq__(self,rhs):
            return self.hash == rhs.hash
        def __hash__(self):
            return hash(self.hash)
        def __ne__(self, rhs):
            return not self == rhs
    '''Takes the contents of a book (in text form) to initialize'''
    def __build_unique_frozen_set(self):
        temp = []
        for i,h in enumerate(self.__importantwords):
            temp.add(Fingerprint.UniqueWordPosition(h,i))
        return temp
    def __init__(self, book, important_words='unique', hash_function=hash):
        if 'unique' == important_words:
            self.__importantwords = self.__get_unique_words(book, hash_function)
        else:
            raise InvalidType('Unsupported method of identifying important words for fingerprint')
        if not len(self.__importantwords):
            raise EmptyBook("Unable to locate alphabetical text to compare.")
        self.__importantset = {}
        for i,c in enumerate(self.__importantwords):
            self.__importantset[c] = i
        #self.__importantset = self.__build_unique_frozen_set()
        self.__booklength = len(book)
        self.hashcheck = Fingerprint.hashcheck_from_options(important_words, hash_function) #Used to verify hash algorithm is the same in case of serialization
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
    def compare_with(self,fp2,method='lcs_custom',quick_threshold=.75,long_threshold=.6,match_threshold=.75):
        if not self.hashcheck == fp2.hashcheck:
            raise DifferentHashes('Attempted to compare two fingerprints that have been created using different hashes')
        if self.__quick_compare(self.__importantset,fp2.__importantset,quick_threshold):
            if method == 'dl':
                score = Fingerprint.__dl_score(self.__importantwords, fp2.__importantwords)
            elif method == 'lcs_custom':
                score = Fingerprint.__lcs_custom(self.__importantwords, fp2.__importantset)
            else:
                raise InvalidType('Attempted to compare fingerprints using an unsupported method')
            if long_threshold < score:
                #We have a book that matches, let's see what the relationship is:
                if min(self.__booklength,fp2.__booklength)/max(self.__booklength, fp2.__booklength) > match_threshold:
                    return 'M', score
                elif self.__booklength > fp2.__booklength:
                    return 'P',score
                else:
                    return 'B',score
            else:
                return 'N',1.0-score
        else:
            return 'N',1.0
    @staticmethod
    def hashcheck_from_options(important_words, hash_function):
        return hash_function(important_words)
        
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
        return array('l',uniquewords)

    '''If given two sets of words, will determine if a relationship is even possible
       A match is possible if the number of similar words make up a certain threshold
       of the shortest book.'''
    @staticmethod
    def __quick_compare(set1, set2, threshold):
        score = len(dict.fromkeys(x for x in set1 if x in set2)) #Get intersection of the two sets
        bestpossible = min(len(set1), len(set2))
        return threshold < (score/bestpossible)
    
    '''This computes a percentage similarity score between two sequences, using the 
       Damerau-Levenshtein distance'''
    @staticmethod
    def __dl_score(seq1, seq2):
        largest = max(len(seq1),len(seq2))
        smallest = min(len(seq1),len(seq2))
        distance = utility.dl_distance(seq1,seq2)
        differences = distance - (largest - smallest) #correct for differences in size
        return 1.0-(differences/smallest)

    '''This function is based on a modified version of a longest common sequence search.
       Since all words are unique within a sequence, we can use a hash lookup instead of
       looping through to find matches.  Also, because we are interested in overall similarity
       more than just the "longest" match, we accumulate any match over a certain length and
       count it towards our score.'''
    @staticmethod
    def __lcs_custom(seq1,set2, threshold = 3):
        totalscore = 0
        bestpossible = min (len(seq1),len(set2))
        nextexpected = 0 #The index of the next character, if the sequences match
        currentscore = 0
        for c1 in seq1:
            c2 = set2.get(c1)
            if c2 == nextexpected: #set2[c1] is our c2
                currentscore = currentscore + 1
                nextexpected = nextexpected + 1
            else:
                if currentscore > threshold:
                    totalscore = totalscore + currentscore
                if c2:
                    nextexpected = c2 + 1
                    currentscore = 1
                else:
                    nextexpected = 0
                    currentscore = 0
        else: #Don't forget whatever score remains at the end!
            if currentscore > threshold:
                totalscore = totalscore + currentscore
        return totalscore / bestpossible