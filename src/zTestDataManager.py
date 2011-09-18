
from __future__ import division #needed so that integer/integer = float
import random
import array
import inspect
from zipfile import ZipFile
import os
import re
import sys


'''This class is used to make 'OCR-like' errors in text files, to make our testing more
   realistic.  It is sloppy test code; please don't use it for anything else.'''
class ErrorMaker:

    def __init__(self,
                 error_rate = 800,
                 single_letter_odds = 10,
                 single_character_odds = 10,
                 single_insert_odds = 10,
                 single_delete_odds = 2,
                 missing_space_odds = 12,
                 garbage_string_odds = 7,
                 garbage_string_min = 5,
                 garbage_string_max = 15,
                 missing_page_odds = 2,
                 repeat_page_odds = 2,
                 per_page_junk = False,
                 per_page_junk_string = "http:/weblike.address/per/page/junk",
                 page_size_min=800,
                 page_size_max=1600):
        self.error_rate = error_rate
        self.errorSingleLetter = single_letter_odds
        self.errorSingleCharacter = single_character_odds
        self.errorSingleDelete = single_insert_odds
        self.errorSingleInsert = single_insert_odds
        self.errorMissingSpace = missing_space_odds
        self.errorGarbageString = garbage_string_odds
        self.garbage_string_min = garbage_string_min
        self.garbage_string_max = garbage_string_max
        self.errorMissingPage = missing_page_odds
        self.errorRepeatPage = repeat_page_odds
        self.per_page_junk = per_page_junk
        self.per_page_junk_string = per_page_junk_string
        self.page_size_min=page_size_min
        self.page_size_max=page_size_max
        random.seed(42) #Because we want consistency in our testing, use a fixed random seed
        self.rebuild_odds_table()
    def __get_random_letter(self):
        return random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    def __get_random_thing(self):
        return random.choice('~`!@#$%^&*(){}:<>?[];')
    '''Functions to introduce error into text; use IntroduceErrors to do so in a uniform way'''
    def __errorSingleLetter(self, text, location):
        counter = 0
        for c in text[location:]:
            if not ' ' == c:
                text[location + counter] = self.__get_random_letter()
                break
            else:
                counter = counter + 1
        return text
    def __errorSingleCharacter(self, text, location):
        text[location] = self.__get_random_thing()
        return text
    def __errorMissingSpace(self, text, location):
        for c in text[location:]:
            if ' ' == c:
                text = text[:location-1] + text[location:]
                break
        return text
    def __errorSingleDelete(self, text, location):
        for c in text[location:]:
            if not ' ' == c:
                text = text[:location-1] + text[location:]
                break
        return text
    def __errorSingleInsert(self, text, location):
        c = array.array ('c', self.__get_random_letter())
        return text[:location] + c + text[location:]
    def __errorGarbageString(self, text, location):
        length = random.randint(self.garbage_string_min,self.garbage_string_max)
        if len(text) > location + length:
            for i in range(length):
                text[location + i] = self.__get_random_letter()
        return text
    def __errorMissingPage(self, text, location):
        length = random.randint(self.page_size_min,self.page_size_max)
        if len(text) > location + length:
            text = text[:location] + text[location+length:]
        return text
    def __errorRepeatPage(self, text, location): #A repeat of the previous page
        length = random.randint(self.page_size_min,self.page_size_max)
        if len(text) > location + length:
            text = text[:location+length] + text[location:]
        return text
    '''Functions to introduce errors in the whole book, rather than a certain location'''
    def __InsertPerPageJunk(self,text, junk): #put some junk, like a web address, on every page
        somejunk = array.array('c')
        somejunk.fromstring(junk)
        currentindex = random.randint(self.page_size_min,self.page_size_max)
        results = []
        while len(text) > currentindex:
            if text[currentindex] == ' ':
                results.append(text[:currentindex+1])
                results.append(somejunk)
                text[currentindex:]
                currentindex = currentindex + random.randint(self.page_size_min,self.page_size_max) + len(somejunk)
            else:
                currentindex = currentindex + 1
        arraytext = array.array('c')
        arraytext.fromstring(''.join(text))
        return arraytext
    
    '''If you change the odds of various erorrs, call this to update the table.
       If this were a production class, this would be the wrong way to do this ;)'''
    def rebuild_odds_table(self):
        oddstotal = 0
        oddstable = []
        members = inspect.getmembers(self)
        for name, value in members:
            if inspect.ismethod(value) and name.find('__error') > -1:
                for varname, varvalue in members:#print varname.find(name[2:])
                    if varname.find(name[13:]) == 0:
                        oddstable.append((value, oddstotal, oddstotal + varvalue))
                        oddstotal += varvalue
                        break
        self.otable = oddstable
        self.ototal = oddstotal

    '''Introduces OCR-like errors in a text.
       text is the text to introduce errors into
       error_rate is how often errors are introduced; approximately 1 error every error_rate bytes
       relative_frequency is a list containing a function that introduces an error at a given location
       and a relative rate at which this function should be called'''             
    def IntroduceErrors(self, text):
        errors = len(text)//self.error_rate
        arraytext = array.array('c')
        arraytext.fromstring(text)
        while errors and self.ototal:
            location = random.randint(0,len(arraytext) -1)
            choice = random.randint(0,self.ototal)
            for er in self.otable:
                if er[1] <= choice and choice < er[2]:
                    arraytext = er[0](arraytext, location)
                    break
            errors = errors - 1
        if self.per_page_junk:
            arraytext = self.__InsertPerPageJunk(arraytext, self.per_page_junk_string)
        return arraytext.tostring()
    
class TestBookManager ():
    '''Create a TestBookManager to manage a collection of test files with duplicates,
       errors, and anthologies to test the code with.
       
       We assume that all books will be unpacked to the testdir, and that the testarchive
       is already there!'''
    def __init__(self, testarchive, testdir):
        self.relationships = {} #Stores the relationships of all books it generates, assuming that there are no pre-existing relationships!
        self.testarchive = testarchive
        self.testdir = testdir
        self.unpacked = False
        self.antcount = 0
        self.usedflags = set()
    def __del__(self):
        #TODO: clean up our books when we're done playing with them.
        pass
    def __mangle_filename(self, filename, newflags=''):
        #This function mangles filenames by sticking flags in brackets on the end.
        #a special exception is the 'o' flag - adding any flag except 'o' will overwrite
        #the 'o' flag.  It returns the new name, and a base name with no mangling or extension
        #(useful for checking to ensure duplicate books are not both added to an anthology!)
        basename, ext = filename.rsplit('.',1)
        matches = re.search('(.+)(\[.+\])$', basename)
        if matches:
            root = matches.group(1)
            flags = matches.group(2)[1:-1]
        else:
            root = basename
            flags = ''
        flags += newflags
        newname = '{0}[{1}].{2}'.format(root, flags, ext)
        if newname in self.usedflags and flags:
            newname = '{0}[{1}2].{2}'.format(root, flags, ext)
        if flags:
            self.usedflags.add(newname)
            return newname
        else: #alternate version just returns the mangle-generated name
            return root
        
    def get_testbooks(self):
        return self.relationships.keys()
    
    def unpack_archive(self, max=0):
        # Unpacks our test files from the archive into the test file directory, and starts
        # building our match list.
        if self.unpacked:
            return
        archive = ZipFile(os.path.join(self.testdir,self.testarchive))
        archivedbooks = archive.namelist()
        if max:
            archivedbooks = random.sample(archivedbooks, max)
        for archivedbook in archivedbooks:
            ofname = self.__mangle_filename(archivedbook, 'o')
            ofname = os.path.join(self.testdir, ofname)
            with open(ofname, 'w') as of:
                inbook = archive.open(archivedbook)
                of.write(inbook.read())
                self.relationships[ofname] = {'matches':set(),'parents':set(),'children':set(), 'ambiguous':set()}
        self.unpacked = True #We only want to unpack once
    
    def make_error_dupes(self,filelist = [], number = 0, errormaker = None):
        #makes some error-ridden files (unless no error maker is passed in; then it just
        #makes copies.)  Either pass a list of files, or a number to randomly select.
        #no validation is done on the names, so be careful and include paths!
        if not filelist:
            if not number > 0:
                print "oops, didn't make any dupes"
                return #We have nothing else to do
            filelist = random.sample(self.relationships, number)
        for file in filelist:
            if errormaker:
                flag = 'e'
            else:
                flag = 'd'
            dupename = self.__mangle_filename(file, flag)
            self.relationships[dupename] = self.relationships[file]
            self.relationships[file]['matches'].add(dupename)
            self.relationships[dupename]['matches'].add(file)
            for child in self.relationships[dupename]['children']:
                #inform our new children of our existance:
                self.relationships[child]['parents'].add(dupename)
            for parent in self.relationships[dupename]['parents']:
                self.relationships[parent]['children'].add(dupename)
            with open(file, 'r') as inf:
                with open(dupename, 'w') as otf:
                    text = inf.read()
                    if errormaker:
                        text = errormaker.IntroduceErrors(text)
                    otf.write(text)
    
    def make_duplicate(self, filelist = [], number = 0):
        # Just a handy alias for making dupes without errors
        return self.make_error_dupes(filelist, number)
    def __check_already_anthologized(self, included, newfile):
        if newfile.find('Anthology') > -1: #We don't (currently) support adding anthologies to anthologies
            return True
        root = self.__mangle_filename(newfile, '')
        for i in included:
            if i.find(root) > -1:
                return True
        else:
            return False
    def __update_anthology_ambiguity(self):
        #Imagine the case where anthology1 inlcudes 2/3 of the books in anthology2, and is twice
        #as long.  Is anthology2 a child of anthology1?  The case is ambiguous, so we won't count
        #it either way.
        antlist = []
        for book in self.relationships.iterkeys():
            if book.find('Anthology') > -1:
                antlist.append(book)
        for ant1 in antlist:
            for ant2 in antlist:
                for child1 in self.relationships[ant1]['children']:
                    for child2 in self.relationships[ant2]['children']:
                        if child1 == child2:
                            self.relationships[ant1]['ambiguous'] = ant2
                            self.relationships[ant2]['ambiguous'] = ant1
    def make_anthology(self, number_to_include = 0):
        text = []
        if not number_to_include:
            print "oops, didn't make an anthology"
            return
        included = set()
        oops = 100 #We don't support adding this many books; so if we get here, just give up.
        antname = os.path.join(self.testdir, 'Anthology{0}[o].txt'.format(self.antcount))
        self.antcount += 1
        while number_to_include and oops:
            oops += -1
            number_to_include += -1
            book = random.choice(self.relationships.keys())
            if not self.__check_already_anthologized(included, book):
                with open(book, 'r') as inf:
                    text.append(inf.read())
                included = self.relationships[book]['matches']
                included.add(book)
                self.relationships[book]['parents'].add(antname)
                for sib in self.relationships[book]['matches']:
                    self.relationships[sib]['parents'].add(antname)
                    #TODO: we'll need more complicated handling if we allow anthologies in anthologies.
        self.relationships[antname] = {'matches':set(),'parents':set(),'children':set(included), 'ambiguous':set()}
        with open(antname, 'w') as of:
            of.write(''.join(text))
    '''Creates a collection of books, duplicates, error duplicates, and archives for
       testing, and stores the relationship information for error checking purposes.
       It uses "reasonable" (read: arbitrary) settings for this process.
       
       original_number is the number of books to choose from the archive
       final_number is the number of books to end up with (if int) or the percentage
       of books to wind up with based on the original (if float)'''
    def make_testcase(self, original_number=0, final_number=1.33):
        relative_odds = {'dupes':1,'errordupes':5,'bigerrordupes':2,'anthologies':2}
        error = ErrorMaker() #default settings should be fine
        bigerror = ErrorMaker(error_rate=300, per_page_junk=True)
        if type(final_number) == float:
            final_number = (original_number * final_number).int()
        print 'Unpacking original books'
        self.unpack_archive(original_number)
        if not original_number:
            original_number = len(self.relationships)
        if original_number < 2 or final_number < original_number:
            print original_number, final_number
            raise ValueError(msg="we need at least two books to check, and we need to wind up with at least as many books as we started with")
        actions = final_number - original_number
        print "creating {0} more duplicate, error, and anthology books".format(actions)
        if actions < 1:
            return
        totalodds = sum(relative_odds.itervalues())
        while actions > 0:
            actions -= 1
            choice = random.randint(0,totalodds-1)
            func = None
            for function, odd in relative_odds.iteritems():
                if choice < odd:
                    func = function
                    break
                else:
                    choice -= odd
            if 'dupes' == func:
                print ',',
                self.make_duplicate(number=1)
            elif 'errordupes' == func:
                print '.',
                self.make_error_dupes(number=1, errormaker=error)
            elif 'bigerrordupes' == func:
                print '*',
                self.make_error_dupes(number=1, errormaker=bigerror)
            elif 'anthologies' ==  func:
                print '@',
                self.make_anthology(random.randint(2,6))
            else:
                raise ValueError()#This shouldn't be possible
    @staticmethod
    def __count_not_present_in_both(known, found, ambiguous, name):
        hit = 0
        ambig = 0
        knownunique = set(known.copy())
        maxhits = len(knownunique)
        foundunique = set(found.copy().keys())
        totalhitscore = 0
        totalfalsehitscore = 0
        misslist = []
        fposlist = []
        for i in known:
            for j in found.iterkeys():
                if i == j:
                    knownunique.remove(i)
                    foundunique.remove(j)
                    hit += 1
                    totalhitscore += found[i]
                    break
        for a in ambiguous: #Don't count ambiguous relationships against our totals
            for j in found:
                if a == j:
                    foundunique.remove(j)
                    ambig += 1
        if name in knownunique: #Don't count missing "ourselves" against us
            knownunique.remove(name)
            maxhits -= 1
        for i in foundunique:
            totalfalsehitscore += found[i]
            fposlist.append((name,i,found[i]))
        for i in knownunique:
            misslist.append((name,i))
        misses = len(knownunique)
        fpos = len(foundunique)
        return misses, fpos, hit, ambig, maxhits, totalhitscore, totalfalsehitscore, misslist, fposlist
    def __get_bookresults_by_txtfile(self, book, library):
        relationships = book.get_relationships()
        txtrelationships = {}
        for hittype in relationships.keys():
            txtrelationships[hittype]={}
            for match in relationships[hittype].keys():
                matchname = library.get_book_uid(match).get_textfilepath()
                txtrelationships[hittype][matchname]=relationships[hittype][match]
        return txtrelationships
                
    def verify_results(self, library):
        self.__update_anthology_ambiguity()
        results = {'duplicates':{'hits':0,'maxhits':0,'misses':0,'false positives':0, 'hitscore':0, 'falsehitscore':0,'misslist':[],'fpos':[]},
                   'parents':{'hits':0,'maxhits':0,'misses':0,'ambiguous':0,'false positives':0, 'hitscore':0, 'falsehitscore':0,'misslist':[],'fpos':[]},
                   'children':{'hits':0,'maxhits':0,'misses':0,'ambiguous':0,'false positives':0, 'hitscore':0, 'falsehitscore':0,'misslist':[],'fpos':[]},
                   'ambiguous':0}
        #Next, look at all our books and compare found relationships to known ones 
        for book in library.book_iter():
            bookpath = book.get_textfilepath()
            foundrelation = self.__get_bookresults_by_txtfile(book, library)
            kmatch = self.relationships[bookpath]['matches']
            kambig = self.relationships[bookpath]['ambiguous']
            fmatch = foundrelation['M']
            miss, fpos, hit, ambig, max, hs, fhs,mlist,fplist = TestBookManager.__count_not_present_in_both(kmatch, fmatch, kambig, bookpath)
            results['duplicates']['misses'] += miss
            results['duplicates']['false positives'] += fpos
            results['duplicates']['hits'] += hit
            results['ambiguous']+= ambig
            results['duplicates']['maxhits'] +=max
            results['duplicates']['hitscore']+= hs
            results['duplicates']['falsehitscore'] += fhs
            if mlist:
                results['duplicates']['misslist'].append(mlist)
            if fplist:
                results['duplicates']['fpos'].append(fplist)
            kmatch = self.relationships[bookpath]['parents']
            fmatch = foundrelation['B']
            miss, fpos, hit, ambig, max, hs, fhs,mlist,fplist = TestBookManager.__count_not_present_in_both(kmatch, fmatch, kambig, bookpath)
            results['parents']['misses'] += miss
            results['parents']['false positives'] += fpos
            results['parents']['hits'] += hit
            results['ambiguous']+= ambig
            results['parents']['maxhits'] += max
            results['parents']['hitscore']+= hs
            results['parents']['falsehitscore'] += fhs
            if mlist:
                results['parents']['misslist'].append(mlist)
            if fplist:
                results['parents']['fpos'].append(fplist)
            kmatch = self.relationships[bookpath]['children']
            fmatch = foundrelation['P']
            miss, fpos, hit, ambig, max, hs, fhs,mlist,fplist = TestBookManager.__count_not_present_in_both(kmatch, fmatch, kambig, bookpath)
            results['children']['misses'] += miss
            results['children']['false positives'] += fpos
            results['children']['hits'] += hit
            results['ambiguous']+= ambig
            results['children']['maxhits'] += max
            results['children']['hitscore']+= hs
            results['children']['falsehitscore'] += fhs
            if mlist:
                results['children']['misslist'].append(mlist)
            if fplist:
                results['children']['fpos'].append(fplist)
        hs = results['duplicates']['hitscore']
        fhs = results['duplicates']['falsehitscore']
        if hs:
            results['duplicates']['hitscore'] = hs / results['duplicates']['hits']
        else:
            results['duplicates']['hitscore'] = 0
        if fhs:
            results['duplicates']['falsehitscore'] = fhs / results['duplicates']['false positives']
        else:
            results['duplicates']['falsehitscore'] = 0
        hs = results['parents']['hitscore']
        fhs = results['parents']['falsehitscore']
        if hs:
            results['parents']['hitscore'] = hs / results['parents']['hits']
        else:
            results['parents']['hitscore'] = 0
        if fhs:
            results['parents']['falsehitscore'] = fhs / results['parents']['false positives']
        else:
            results['parents']['falsehitscore'] = 0
        hs = results['children']['hitscore']
        fhs = results['children']['falsehitscore']
        if hs:
            results['children']['hitscore'] = hs / results['children']['hits']
        else:
            results['children']['hitscore'] = 0
        if fhs:
            results['children']['falsehitscore'] = fhs / results['children']['false positives']
        else:
            results['children']['falsehitscore'] = 0
        return results
    def print_formatted_results(self, results):
        print '=============================================================='
        print 'Duplicate results:'
        print 'Hits: {0} out of {1} ({2:.1%})'.format(results['duplicates']['hits'], results['duplicates']['maxhits'], results['duplicates']['hits']/results['duplicates']['maxhits'])
        print 'Average hit score: {0:.1%}'.format(results['duplicates']['hitscore'])
        print 'False positives: {0}'.format(results['duplicates']['false positives'])
        print 'Average false positive score: {0:.1%}'.format(results['duplicates']['falsehitscore'])
        print 'Misses:.......................................................'
        print ''.join(map(lambda x:'{0} missed matching {1}\n'.format(x[0][0],x[0][1]), results['duplicates']['misslist']))
        print 'False Positives:..............................................'
        print ''.join(map(lambda x:'{0} falsely matched {1} with score {2:.1%}\n'.format(x[0][0],x[0][1], x[0][2]), results['duplicates']['fpos']))
        print '=============================================================='
        print 'Superset results:'
        print 'Hits: {0} out of {1} ({2:.1%})'.format(results['parents']['hits'], results['parents']['maxhits'], results['parents']['hits']/results['parents']['maxhits'])
        print 'Average hit score: {0:.1%}'.format(results['parents']['hitscore'])
        print 'False positives: {0}'.format(results['parents']['false positives'])
        print 'Average false positive score: {0:.1%}'.format(results['parents']['falsehitscore'])
        print 'Misses:.......................................................'
        print ''.join(map(lambda x:'{0} missed matching {1}\n'.format(x[0][0],x[0][1]), results['parents']['misslist']))
        print 'False Positives:..............................................'
        print ''.join(map(lambda x:'{0} falsely matched {1} with score {2:.1%}\n'.format(x[0][0],x[0][1], x[0][2]), results['parents']['fpos']))
        print '=============================================================='
        print 'Subset results:'
        print 'Hits: {0} out of {1} ({2:.1%})'.format(results['children']['hits'], results['children']['maxhits'], results['children']['hits']/results['children']['maxhits'])
        print 'Average hit score: {0:.1%}'.format(results['children']['hitscore'])
        print 'False positives: {0}'.format(results['children']['false positives'])
        print 'Average false positive score: {0:.1%}'.format(results['children']['falsehitscore'])
        print 'Misses:.......................................................'
        print ''.join(map(lambda x:'{0} missed matching {1}\n'.format(x[0][0],x[0][1]), results['children']['misslist']))
        print 'False Positives:..............................................'
        print ''.join(map(lambda x:'{0} falsely matched {1} with score {2:.1%}\n'.format(x[0][0],x[0][1], x[0][2]), results['children']['fpos']))
        print '=============================================================='
            
            

        
            
