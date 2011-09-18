'''The library is the program's store of Book objects.  It takes care
   of managing them and serializing/deserializing them.'''

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
            if textfile == book.get_textfilepath():
                return book
        return None
    def get_book_count(self):
        return len(self.__books_by_uuid)
    def book_iter(self):
        #This can probably be invalidated if books are added during use; only use it after
        #all books are added to the library
        for book in self.__books_by_uuid.itervalues():
            yield book
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
    def update_book_uid(self,*args):
        for id in args:
            pass #hopefully this won't be needed to ensure consistency
    def print_pretty_tree(self):
        class Node():
            def __init__(self):
                self.books=[]
                self.children=[]
                self.parents=[]
            def __str__(self):
                text  = "-----------------------------------------------------------------\n"
                text += "Matches:\n"
                text += self.books.__str__()
                text += "\nChilren:\n"
                text += self.children.__str__()
                text += "\nParents:\n"
                text += self.parents.__str__()
                text += "\n-----------------------------------------------------------------\n"
                return text
        nodelist = []
        unmatched = []
        done = set()
        for book in self.__books_by_uuid.values():
            if book in done:
                pass
            else:
                relate = book.get_relationships()
                if not len(relate['M']) and not len(relate['P']) and not len(relate['B']):
                    unmatched.append(book.get_textfilepath())
                else:
                    node = Node()
                    node.books.append(book.get_textfilepath())
                    for uid in relate['M'].iterkeys():
                        mbook = self.get_book_uid(uid)
                        node.books.append(mbook.get_textfilepath())
                        done.add(mbook)
                    for uid in relate['P'].iterkeys():
                        mbook = self.get_book_uid(uid)
                        node.children.append(mbook.get_textfilepath())
                    for uid in relate['B'].iterkeys():
                        mbook = self.get_book_uid(uid)
                        node.parents.append(mbook.get_textfilepath())
                    nodelist.append(node)
        text = ""
        for i in nodelist:
            text += i.__str__()
        text += 'Unmatched Files:\n'
        for i in unmatched:
            text+= i.__str__()
        return text
            
            
    