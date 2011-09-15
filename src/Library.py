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
    def get_book_uid(self, id):
        return self.__books_by_uuid.get(id)
    def get_book_cid(self, id):
        return self.__books_by_uuid.get(self.__uuid_by_calibre_id.get(id))
    def get_book_textfile(self, textfile): #This is used mostly for testing, so is slow
        for book in self.__books_by_uuid.values():
            if textfile == book.matchtextfile(textfile):
                return book
        return None
    def delete_book_uid(self,id):
        book = self.get_book_uid(id)
        if book:
            if book.calibreid:
                for uuid in self.__uuid_by_calibre_id.iteritems():
                    if uuid == id:
                        del self.__uuid_by_calibre_id[uuid]
            del self.__books_by_uuid[id]
                        
        else:
            pass #declare "success" - after all, the book is no longer here, right?
    def update_book_uid(self,idlist):
        if 1 == len(idlist):
            idlist = (idlist,)
        for id in idlist:
            pass #hopefully this won't be needed to ensure consistency
    