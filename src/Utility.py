
from array import array
import time

def average_iterable(iter):
    total = 0
    for i in iter:
        total += i
    return total/len(iter)

'''This function calculates the Damerau-Levenshtein distance between sequences.'''
def dl_distance(seq1, seq2):
    #http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
    return thisrow[len(seq2) - 1]  

'''Will map function to each pair that can be generated from the (one dimensional!) array
   "all." The function should return C(ontinue), S(leeping), or Q(uit).  The function
   will compare the first element with all others, until it is told to "sleep" - then
   it will begin comparing the second element with all others.  Once it has finished with
   a set, it will go back and work on finishing any previously unfinished sets.  This allows
   comparisons to happen even if not all the elements in 'all' are not yet generated.  allsize
   is the size that "all" will grow to.  It can be larger than necessary; however the
   comparison function would have to call "stop."
   
   the two items to be compared will be the first positional arguments to the function.'''
def compare_all_despite_starvation(all, allsize, function, sleep, *args, **kwargs):
    progress = array('L', [1 for unused in xrange(allsize)]) #create an array large enough to hold a counter for each item
    i = 0
    status = 'C'
    any_unfinished = False
    compares = 0;
    while True:
        uninterrupted = True
        j = max(progress[i], i+1)
        while uninterrupted and j < allsize:
            status = function(all[i], all[j], args, kwargs)
            if status == 'Q':
                break
            elif status == 'S':
                uninterrupted = False
                any_unfinished = True
            else:
                compares += 1
            j = j + 1
        if status == 'S':
            progress[i] =  j - 1
        elif status == 'Q':
            break #Python needs either a do-while loop, or a multilevel break to avoid this second comparison
        else:
            progress[i] = allsize+1
        i += 1
        if i > (allsize-1):
            if not any_unfinished:
                break
            else:
                if sleep:
                    time.sleep(sleep)
                any_unfinished = False
                i = 0
''' For when we start looking in to minhash, here's a way to make an arbitrary number
of hash functions: (http://stackoverflow.com/questions/2255604/hash-functions-family-generator-in-python)

import random

_memomask = {}

def hash_function(n):
  mask = _memomask.get(n)
  if mask is None:
    random.seed(n)
    mask = _memomask[n] = random.getrandbits(32)
  def myhash(x):
    return hash(x) ^ mask
  return myhash
'''
                
class MaskList():
    def __init__(self, max_masks):
        self.masks = {}
        import random
        #random.seed(12345) #The same as the combination to my luggage!
        for mask in xrange(0,max_masks):
            #self.masks[mask] = random.getrandbits(64)
            self.masks[mask] = 1
            
myMasks = MaskList(100)
