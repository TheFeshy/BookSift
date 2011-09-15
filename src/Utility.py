
from array import array
import threading
import time

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
            j = j + 1
        if status == 'S':
            progress[i] =  j - 1
        elif status == 'Q':
            break #Python needs either a do-while loop, or a multilevel break to avoid this second comparison
        else:
            progress[i] = allsize+1
        i = i + 1
        if i > (allsize-1):
            if not any_unfinished:
                break
            else:
                if sleep:
                    time.sleep(sleep)
                any_unfinished = False
                i = 0

def slowarray(array, l):
    for i,c in enumerate(array[0]):
        with l:
            array[0][i] = i
        time.sleep(.01)
            
def testfunc(n1, n2, result, bogus):
    retval = 'C'
    lock = result[0][1]
    with lock:
        if n1 < 0 or n2 < 0:
            retval = 'S'
        else:
            result[0][0][0] = result[0][0][0] + n1 + n2
    return retval

if __name__ == '__main__':
    testarray = [x for x in range(100)]
    total = 0 #We will test that all pairs are summed by getting the total of all pair additions
    paircount = 0
    for i, n1 in enumerate(testarray):
        for j, n2 in enumerate(testarray):
            if i < j:
                paircount = paircount +1
                total = total + n1 + n2
    print total
    testarray2 = [-1 for unused in range(100)]
    l = threading.Lock()
    t = threading.Thread(target=slowarray, args=((testarray2,),l))
    t.start()
    result = [0,]
    compare_all_despite_starvation(testarray2, len(testarray2), testfunc, 0.01, (result,l))
    print result.pop()
    