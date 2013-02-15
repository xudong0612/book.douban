# -*- coding: UTF-8 -*-
import MySQLdb
from math import sqrt
from math import log

class Movement:
    def __init__(self, host, user, psw, dbname):
        self.con = MySQLdb.connect(host, user, psw, dbname, charset='utf8')
        self.cur = self.con.cursor()
        self.prefs = dict()
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
        
    def GetMovementByUser(self, userid):
        books = dict()
        self.cur.execute('SELECT title, pic, status, left(date, 10) FROM douban.books_list \
            left join douban.books_book on douban.books_book.id = douban.books_list.book_id \
                where user_id = %d order by date desc;' % userid)
        results = self.cur.fetchall()
        for book in results:
            #print book[0], book[1], book[2], book[3]
            if books.has_key(book[3]):
                subdict = books[book[3]]
            else:
                subdict = {}
            subdict[book[0]] = {"pic":book[1], "status":book[2] }
            books[book[3]] = subdict
            
        #print books
        
        for date in books.keys():
            print date
            for title in books.get(date):
                print title, books.get(date)[title]['pic'], books.get(date)[title]['status']
        return books
            #for title, pic, status in book.items():
            #    print title, pic, status
            
        
#m = Movement('localhost', 'root', 'hehe', 'douban')
#m.GetMovementByUser(1)
    