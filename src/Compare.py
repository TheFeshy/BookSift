'''
Compare

This is the collection of functions and parameters that define how book to book comparisons
are carried out.  A global Compare Parameters list is created at the end that defines the
set of searches that are carried out.  Each search is tried in order until the match is
either above the slow_cutoff, or below the min_score.
'''

from __future__ import division #needed so that integer/integer = float
import Utility
import math
import Cfg
if Cfg.myOptions.useC:
    import OptimizeCompare
   
class MinHashParams():
    def __init__(self,
                 minhash_tables,
                 minhash_threshold):
        self.minhash_tables = minhash_tables
        self.minhash_threshold = minhash_threshold

myMinHashParams = MinHashParams(minhash_tables = 50,
                                minhash_threshold = 1)

class CompareParams():
    '''Defines a set of comparison parameters to use.  Each parameter is a function, and returns a
       value.'''
    def __init__(self, 
                 min_score = None, 
                 slow_cutoff = None,
                 meaningful_length = None,
                 allowed_consecutive_errors = None,
                 allowed_displacement_error = None,
                 adjust_score = None,
                 count_misses = True,
                 search_method = None):
        '''Creates a set of parameters defining a comparison.
           
           * min_score is the score below which the search is assumed to be negative.
             Given size1, size2, seqsize1, and seqsize2 as parameters. Returns 0.0 to 1.0
           * slow_cutoff is the score above which the search is assumed to be positive.  
             Scores between min_score and slow_cutoff are assumed ambiguous, and will be
             re-compared with another search.  Given size1, size2, seqsize1, and seqsize2
             as parameters.  Returns 0.0 to 1.0
           * meaningful_length is a parameter passed to the search.  It is given size1, size2, 
             seqsize1, seqsize2, and allowed_consecutive_errors as parameters. Returns a small integer.
           * allowed_consecutive_errors is the number of sequential errors or other errors a search should
             accept.  It is passed to the search method.  It is passed size1, size2, seqsize1,
             and seqsize2.  Returns a small integer.
           * adjust_score is the score reported to the user, scaled to a value consistent
             with the other comparisons.  It is given the calculated score, size1, size2,
             seqsize1, and seqsize2.
           * search_method compares two fingerprints, and computes a score.  It is given
             sequence1, set1, sequence2, set2, meaningful_length, and allowed_consecutive_errors.
             Returns a score from 0.0 to 1.0
             '''  
        self.min_score = min_score 
        self.slow_cutoff = slow_cutoff
        self.meaningful_length = meaningful_length
        self.allowed_consecutive_errors = allowed_consecutive_errors
        self.allowed_displacement_error = allowed_displacement_error
        self.adjust_score = adjust_score 
        self.count_misses = count_misses
        self.search_method = search_method 
        
        
def fixed_min_score(size1, size2, seqsize1, seqsize2):
    return .25

def variable_min_score(size1,size2,seqsize1,seqsize2):
    maxatone = .5
    minatzero = .4
    ratio = min(size1,size2)/max(size1,size2)
    return (ratio * ratio *(maxatone - minatzero)) + minatzero

def fixed_slow_cutoff(size1, size2, seqsize1, seqsize2):
    return 0.0

def fixed_meaningful_length(size1, size2, seqsize1, seqsize2, allowed_consecutive_errors):
    return 6

def fixed_allowed_consecutive_error(size1, size2, seqsize1, seqsize2):
    return 9

def fixed_allowed_distance_error(size1, size2, seqsize1, seqsize2):
    return 9

def unchanged_score(score, size1, size2, seqsize1, seqsize2):
    return score
'''
def fixed_min_score(size1, size2, seqsize1, seqsize2):
    return .62

def fixed_slow_cutoff(size1, size2, seqsize1, seqsize2):
    return 0.0

def fixed_meaningful_length(size1, size2, seqsize1, seqsize2, allowed_consecutive_errors):
    return 0

def fixed_allowed_consecutive_errors(size1, size2, seqsize1, seqsize2):
    return 0

def unchanged_score(score, size1, size2, seqsize1, seqsize2):
    return score
'''
class PerfCounters():
    def __init__(self):
        self.fallback_compare = {}
        self.hits = 0
        self.misses = 0
        self.quickcompares = 0
        self.highest_miss = 0
    def reset_counters(self):
        self.fallback_compare.clear()
        self.hits = 0
        self.misses = 0
        self.quickcompares = 0
        self.highest_miss = 0

gPerfCounters = PerfCounters()
        

'''This function is based on a modified version of a longest common sequence search.
       Since all words are unique within a sequence, we can use a hash lookup instead of
       looping through to find matches.  Also, because we are interested in overall similarity
       more than just the "longest" match, we accumulate any match over a certain length and
       count it towards our score.
       
       meaningful_length is the number of consecutive characters to be considered a meaningful
       match
       quick_threshold is the percentage of words that must be present in both sets'''

def tcs_custom(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors, count_misses, tcs, early_exit=True):
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
    errors_remain = allowed_errors
    miss = int(len(seq1) *(1-min_score))
    errors_reset = False #we haven't had our error quota hit yet
    for i1 in xrange(len(shortseq)):
        c1 = shortseq[i1]
        i2 = longset.get(c1)
        if i2 and abs((i2 - nextexpected)) <= allowed_errors: #"Match" found, close enough to where it was expected.
            currentscore += 1
            nextexpected += 1
            errors_remain = allowed_errors #Reset our error tally
            errors_reset = True
        else: #"No Match" found
            if errors_remain: #We didn't match, but we are allowed not to still
                if count_misses:
                    currentscore += 1
                nextexpected += 1    
                errors_remain -= 1       
            else: #We didn't match and have used up all our consecutive errors
                if errors_reset:
                    nextexpected -= allowed_errors #Move back to where we had misses
                    i1 -= allowed_errors #Move back to where things started to go wrong and start again
                    currentscore -= allowed_errors #Don't count the errors we had so far getting here    
                    errors_reset = False
                else:
                    nextexpected -= 1
                    i1 -= 1
                c1 = shortseq[i1]
                i2 = longset.get(c1) #Reset our "found" position to the position after our last match
                miss -= 1 
                if not miss and early_exit:
                    return 0
                if currentscore > meaningful_length: #We no longer match, but remember how much we have matched so far
                    if tcs:
                        totalscore += currentscore
                    elif currentscore > totalscore:
                        totalscore = currentscore
                if i2: #If we at least found a character somewhere in the next sequence, start matching from there
                    nextexpected = i2 + 1
                    currentscore = 1
                else: #If we did not find our character somewhere, we can't start matching again yet.
                    nextexpected = 0
                    currentscore = 0
    else: #Don't forget whatever score remains at the end!
        if currentscore > meaningful_length:
            totalscore = totalscore + currentscore
    return totalscore / bestpossible

def tcs_redux(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_consecutive_errors, allowed_distance_error, count_misses):
    if len(seq1) < len(seq2):
        shortseq = seq1
        longset = set2
    else:
        shortseq = seq2
        longset = set1
    totalscore = 0
    bestpossible = len(shortseq)
    currentscore = 0
    errors_remain = -1
    nextexpected = -100
    initialmatch = longset.get(shortseq[0])
    if initialmatch:
        nextexpected = initialmatch
    for index1, word1 in enumerate(shortseq):
        index2 = longset.get(word1)
        if index2 and (abs(index2 - nextexpected)) < allowed_distance_error:
            #hit!
            currentscore += 1
            nextexpected = index2 + 1
            errors_remain = allowed_consecutive_errors
        else:
            if errors_remain > 0:
                #pretend it's a hit and see where it gets us:
                if count_misses:
                    currentscore += 1
                if index2:
                    nextexpected = index2 +1
                else:
                    nextexpected += 1
                errors_remain -= 1
            else:
                if 0 == errors_remain:
                    #We flubbed it; back up and try again!
                    if count_misses:
                        currentscore -= allowed_consecutive_errors
                    index1 -= allowed_consecutive_errors
                    errors_remain = -1
                    index2 = longset.get(shortseq[index1])
                    #print index2
                    if currentscore > meaningful_length:
                        totalscore += currentscore
                if index2: #this is a miss for our current count, but a hit somewhere!
                    nextexpected = index2+1
                    currentscore = 1
                    errors_remain = allowed_consecutive_errors
                else:
                    nextexpected = -100
                    currentscore = 0
    else:
        if currentscore > meaningful_length:
            totalscore += currentscore
    return totalscore / bestpossible
        

def count_small_misses_lcs(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors):
    score = tcs_custom(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors, True, False, False)
    if not score:
        return 0 #Handle special case; log0 not defined.
    score = score * min(len(seq1),len(seq2))
    print "LCS:", score, len(seq1), len(seq2)
    score = math.log(score)/(math.log(len(seq1)+len(seq2)-score))
    return score
    #return math.log(score)/math.log(min(len(seq1),len(seq2)))

def count_small_misses_tcs(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors):
    return tcs_custom(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors, True, True)

def dl_compare(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors):
    distance = Utility.dl_distance(seq1, seq2)
    len1 = len(seq1)
    len2 = len(seq2)
    doesntcount = max(len1,len2) - min(len1,len2)
    return 1.0 -((distance-doesntcount)/min(len(seq1),len(seq2)))

'''Here we set the global search parameters.  This is a list of searches to be tried,
   in order, until the results are either < min_score, or > slow_cutoff.'''
'''
gCompareParams = [CompareParams(min_score = fixed_min_score, 
                                slow_cutoff = fixed_slow_cutoff,
                                meaningful_length = fixed_meaningful_length,
                                allowed_consecutive_errors = fixed_allowed_consecutive_errors,
                                adjust_score = unchanged_score,
                                search_method = count_small_misses_lcs),]'''

def UseCSearch(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_consecutive_errors, allowed_distance_error, count_misses):
    if len(seq1) < len(seq2):
        shortseq = seq1
        longset = set2
    else:
        shortseq = seq2
        longset = set1
    return OptimizeCompare.compare(shortseq, longset, meaningful_length, allowed_consecutive_errors, allowed_distance_error)

if Cfg.myOptions.useC:
    gCompareParams = [CompareParams(min_score = variable_min_score, 
                                slow_cutoff = fixed_slow_cutoff,
                                meaningful_length = fixed_meaningful_length,
                                allowed_consecutive_errors = fixed_allowed_consecutive_error,
                                allowed_displacement_error = fixed_allowed_consecutive_error,
                                adjust_score = unchanged_score,
                                count_misses = True,
                                search_method = UseCSearch),]
else:    
    gCompareParams = [CompareParams(min_score = variable_min_score, 
                                slow_cutoff = fixed_slow_cutoff,
                                meaningful_length = fixed_meaningful_length,
                                allowed_consecutive_errors = fixed_allowed_consecutive_error,
                                allowed_displacement_error = fixed_allowed_consecutive_error,
                                adjust_score = unchanged_score,
                                count_misses = True,
                                search_method = tcs_redux),]
