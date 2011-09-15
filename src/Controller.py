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

import time

from Exceptions import NotInitialized
import Book
     
'''This thread handles making sure the book fingerprints get generated.'''     
def fingerprint_initializer(library, bookids):
    for id in bookids:
        book = library.get_book_uid(id)
        book.initialize_text_data()
        library.update_book_uid(book.id)
        #TODO: put in "exit command" code

'''This thread handles comparing all the books with each other.'''
def book_comparator(library, bookids):
    for i, id1 in enumerate(bookids):
        for j, id2 in enumerate(bookids):
            if i < j:
                book1 = library.get_book_uid(id1)
                book2 = library.get_book_uid(id2)
                compared = False
                while not compared:
                    try:
                        result = book1.compare_with(book2)
                        compared = True
                        if not 'N' == result[0]:
                            library.update_book_uid((book1.id, book2.id))
                    except (NotInitialized):
                        time.sleep(1)

'''Takes an iterable of bookids, and does all procsesing / thread management of said processing.'''
def process_books(library, calibre_ids, book_text_files=None, multi_thread=False):
    for id in calibre_ids:
        if not library.get_book_cid(id):
            library.add_book(Book.Book(calibreid=id))
    for id in book_text_files:
        if not library.get_book_textfile(id):
            library.add_book(Book.Book(textfile=id))
    
   
