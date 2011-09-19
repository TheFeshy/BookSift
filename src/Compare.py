'''
Compare

This is the collection of functions and parameters that define how book to book comparisons
are carried out.  A global Compare Parameters list is created at the end that defines the
set of searches that are carried out.  Each search is tried in order until the match is
either above the slow_cutoff, or below the min_score.
'''

from __future__ import division #needed so that integer/integer = float

class CompareParams():
    '''Defines a set of comparison parameters to use.  Each parameter is a function, and returns a
       value.'''
    def __init__(self, 
                 min_score = None, 
                 slow_cutoff = None,
                 meaningful_length = None,
                 allowed_errors = None,
                 adjust_score = None,
                 search_method = None):
        '''Creates a set of parameters defining a comparison.
           
           * min_score is the score below which the search is assumed to be negative.
             Given size1, size2, seqsize1, and seqsize2 as parameters. Returns 0.0 to 1.0
           * slow_cutoff is the score above which the search is assumed to be positive.  
             Scores between min_score and slow_cutoff are assumed ambiguous, and will be
             re-compared with another search.  Given size1, size2, seqsize1, and seqsize2
             as parameters.  Returns 0.0 to 1.0
           * meaningful_length is a parameter passed to the search.  It is given size1, size2, 
             seqsize1, seqsize2, and allowed_errors as parameters. Returns a small integer.
           * allowed_errors is the number of sequential errors or other errors a search should
             accept.  It is passed to the search method.  It is passed size1, size2, seqsize1,
             and seqsize2.  Returns a small integer.
           * adjust_score is the score reported to the user, scaled to a value consistent
             with the other comparisons.  It is given the calculated score, size1, size2,
             seqsize1, and seqsize2.
           * search_method compares two fingerprints, and computes a score.  It is given
             sequence1, set1, sequence2, set2, meaningful_length, and allowed_errors.
             Returns a score from 0.0 to 1.0
             '''  
        self.min_score = min_score 
        self.slow_cutoff = slow_cutoff
        self.meaningful_length = meaningful_length
        self.allowed_errors = allowed_errors
        self.adjust_score = adjust_score 
        self.search_method = search_method 
        
        
def fixed_min_score(size1, size2, seqsize1, seqsize2):
    return .6

def fixed_slow_cutoff(size1, size2, seqsize1, seqsize2):
    return 0.0

def fixed_meaningful_length(size1, size2, seqsize1, seqsize2, allowed_errors):
    return 3

def fixed_allowed_errors(size1, size2, seqsize1, seqsize2):
    return 0

def unchanged_score(score, size1, size2, seqsize1, seqsize2):
    return score

class PerfCounters():
    def __init__(self):
        self.fallback_compare = {}
        self.hits = 0
        self.misses = 0
        self.quickcompares = 0
    def reset_counters(self):
        self.fallback_compare.clear()
        self.hits = 0
        self.misses = 0
        self.quickcompares = 0

gPerfCounters = PerfCounters()
        

'''This function is based on a modified version of a longest common sequence search.
       Since all words are unique within a sequence, we can use a hash lookup instead of
       looping through to find matches.  Also, because we are interested in overall similarity
       more than just the "longest" match, we accumulate any match over a certain length and
       count it towards our score.
       
       meaningful_length is the number of consecutive characters to be considered a meaningful
       match
       quick_threshold is the percentage of words that must be present in both sets'''

def tcs_custom(seq1 ,set1, seq2, set2, min_score, meaningful_length, allowed_errors):
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
    miss = int(len(seq1) *(1-min_score))
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

'''Here we set the global search parameters.  This is a list of searches to be tried,
   in order, until the results are either < min_score, or > slow_cutoff.'''
gCompareParams = [CompareParams(min_score = fixed_min_score, 
                                slow_cutoff = fixed_slow_cutoff,
                                meaningful_length = fixed_meaningful_length,
                                allowed_errors = fixed_allowed_errors,
                                adjust_score = unchanged_score,
                                search_method = tcs_custom),]
