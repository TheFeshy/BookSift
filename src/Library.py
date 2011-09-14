'''The library is the program's store of Book objects.  It takes care
   of managing them and serializing/deserializing them.'''

import Book

class Library():
    def __init__(self):
        self.__books_by_uuid = {}
        self.__uuid_by_calibre_id = {}
    def add_book(self, book):
        self.__books_by_uuid[book.id]=book
        if book.calibreid:
            self.__uuid_by_calibre_id[book.calibreid] = book.id
        
    