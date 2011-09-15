'''This contains the thread controller and the task threads that do the actual work
   of scanning and comparing books.
   
   A brief note on threading/processing:
     Python multiprocessing is the only way to truly take advantage of multiple cores,
     however it does not handle large amounts of shared memory (especially mutable 
     memory) in a platform-independent way.  This means either huge overhead from
     pickling our data from thread to thread and massive memory consumption as we
     duplicate the data store, or...
     
     We just use Threads instead.  While the file comparisons are heavily processor
     bound, the text conversions and web lookups are largely i/o bound.  This should
     allow us to not waste too much time.  It still won't saturate your eight-core
     hypterthreaded beast though.'''


from Exceptions import NotInitialized, TBD
import Book
import Utility
     
'''This thread handles making sure the book fingerprints get generated.'''     
def fingerprint_initializer(library, bookids):
    for id in bookids:
        book = library.get_book_uid(id)
        book.initialize_text_data()
        library.update_book_uid(book.id)
        #TODO: put in "exit command" code

def book_compare_helper(bookid1, bookid2, args, kwargs):
    library = args[0]
    book1 = library.get_book_uid(bookid1)
    book2 = library.get_book_uid(bookid2)
    try:
        result = book1.compare_with(book2)
        if not 'N' == result[0]:
            library.update_book_uid((book1.id, book2.id))
    except (NotInitialized):
        return 'S' #If we hit an unitialized book, work on something else until it's ready

'''This thread handles comparing all the books with each other.'''
def book_comparator(library, bookids):
    Utility.compare_all_despite_starvation(bookids, len(bookids), book_compare_helper, 0, library)
    #TODO: put in "exit command" code

'''Takes an iterable of bookids, and does all procsesing / thread management of said processing.'''
def process_books(library, calibre_ids=None, book_text_files=None, multi_thread=False):
    bookids = []
    if calibre_ids:
        for id in calibre_ids:
            book = library.get_book_cid(id)
            if not book:
                book = Book.Book(calibreid=id)
                library.add_book(book)
            bookids.add(book.id)
    if book_text_files:
        for id in book_text_files:
            book = library.get_book_textfile(id)
            if not book:
                book = Book.Book(textfile=id)
                library.add_book(book)
            bookids.append(book.id)
    if not multi_thread:
        #Just run through our tasks serially
        fingerprint_initializer(library, bookids)
        book_comparator(library, bookids)
    else:
        raise TBD('Multithreading is not yet implimented')
        
    
   
