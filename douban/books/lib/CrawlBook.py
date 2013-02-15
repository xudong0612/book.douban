# -*- coding: UTF-8 -*-
import httplib2
import urllib
import json
import MySQLdb
import collections
from bs4 import BeautifulSoup
import datetime
import re
from decimal import *
import time
d = collections.defaultdict(lambda:1)
ignorewords = set(['?', '、', '。', '“', '《', '》', '”', '！', '(', ')', '[', ']','？', '，', '（', '）', '*', '.'])
h = httplib2.Http()
mark = {"en":1, "zh":2}
path = "/static/"
class crawler:
    def __init__(self, host, user, psw, dbname, filename='SogouLabDic.dic'):
        f = open(filename, 'r')
        total = 0
        while True:
            line = f.readline()
            if not line: break
            word, freq = line.split('\t')[0:2]
            total += int(freq) + 1#smooth
            try:
                d[word.decode('gbk')] = int(freq) + 1
            except:
                d[word] = int(freq) + 1
        f.close()
        d['_t_'] = total
        self.con = MySQLdb.connect(host, user, psw, dbname, charset='utf8')
        self.cur = self.con.cursor()   
    
    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()
        
    def updatebook_intro(self):        
        self.cur.execute('select id, url from books_urllist')        
        urls = list(self.cur.fetchall())  # print urls                
        for id, url in urls:            
            time.sleep(2)            
            print id, url            #print url[0]            
            newurl = url.replace('http://book.douban.com/subject/', 'http://api.douban.com/v2/book/')            
            print newurl            
            response, content = h.request(newurl + '?apikey=0b1e91d5cc2acd80215bb58164806880')            
            string = bytes.decode(content)            
            content = json.loads(string)            
            summary = content["summary"]            
            try:                
                self.cur.execute("update books_book set content_profile ='%s' where urlid=%d" % (summary,id))            
            except:                
                continue        
        self.dbcommit()

    
    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self, table, field, value, exactly=0, createnew=True):
        self.cur.execute(
            "select id from %s where %s='%s'" % (table, field, value))
        res = self.cur.fetchone()
        if res == None:
            if table=='books_urllist':
                self.cur.execute(
                    "insert into %s (%s) values('%s')" % (table, field, value))
            elif table=='books_wordlist':
                self.cur.execute(
                    "insert into %s (word, isexactly) values('%s', %d)" % (table, value, exactly))
            elif table=='books_tag':
                self.cur.execute(
                    "insert into %s (%s) values('%s')" % (table, field, value))
            return self.cur.lastrowid
        else:
            return res[0]
    
    # Index an individual page
    def addtoindex(self, url, string):
        url = url.replace('http://api.douban.com/v2/book/', 'http://book.douban.com/subject/')
        if self.isindexed(url):
            return
        print 'Indexing ' + url
        
        urlid = self.getentryid('books_urllist', 'url', url)
        #print url
        text, ISBN = self.gettextonly(string, urlid)
        #words = self.separatechwords(text.decode('utf8'))
        
        zh_en_group=self.split_zh_en(text.decode('utf8'))
        #print urlid
        for st in zh_en_group:
            if st[0] == mark["en"]:
                words = self.separateenwords(st[1] + u'')
                for i in range(len(words)):
                    word = words[i]
                    #print word
                    if word in ignorewords:
                        continue
                    wordid = self.getentryid('books_wordlist', 'word', word)
                    self.cur.execute("insert into books_wordlocation(urlid, wordid, location) \
                          values (%d, %d, %d)" % (urlid, wordid, i))                 
            else:
                words = self.separatechwords(st[1].strip().decode('utf8'))
                for i in range(len(words)):
                    word = words[i]
                    #print word
                    if word in ignorewords:
                        continue
                    wordid = self.getentryid('books_wordlist', 'word', word)
                    self.cur.execute("insert into books_wordlocation(urlid, wordid, location) \
                          values (%d, %d, %d)" % (urlid, wordid, i))
        wordid = self.getentryid('books_wordlist', 'word', ISBN, 1)
        self.cur.execute("insert into books_wordlocation(urlid, wordid, location) \
            values (%d, %d, %d)" % (urlid, wordid, i))    

    # Extract the text from an HTML page
    def gettextonly(self, string, urlid):
        #print string
        self.cur.execute(
            "select * from books_book where urlid=%d" % urlid)
        res = self.cur.fetchone()
        #print urlid, title, authors, ISBN
        if res == None:
            content = json.loads(string)
            #print content
            title = content["title"]
            authors = ''
            for i in range(len(content["author"])):
                authors + content["author"][i] + ' '
            authors = content["author"][0]
            publisher = content["publisher"]
            pubdate = content["pubdate"]
            #author_intro = content["author_intro"]
            price = ''
            price = content["price"]
            pages = content["pages"]
            if pages =='':
                pages = '0'
            ISBN = content["isbn13"]
            #rating = content["rating"]["average"]
            #summary = content["summary"]
            urlname = content["images"]["medium"]
            filename = urlname.split("/")[-1]
            url = path + filename
            urllib.urlretrieve(urlname, "/home/hehe/eclipse/workspace/douban/DoubanImages/" + filename)
            insert = "insert into books_book(title, author, publication, publication_date, evaluation, pic, pages, price, ISBN, urlid, typeid) \
                values ('" + title + "', '" + authors + "', '" + publisher + "', '" + pubdate + "', '0.0', '" + url + \
                   "', " + pages + ", '" + price + "', '" + ISBN + "', " + str(urlid) +", 5)"
            #print insert
            self.cur.execute(insert)
            book_id = self.cur.lastrowid
            #tagStr = ''
            for i in range(len(content["tags"])):
                #tagStr += content["tags"][i]["name"] + ' '
                tagid = self.getentryid('books_tag', 'contents', content["tags"][i]["name"])
                self.cur.execute('insert into books_tagging(tag_id, user_id, book_id) values (%d, %d, %d)' % (tagid, 1, book_id))
            
            return title + ' ' + authors, ISBN
        else:
            return
    
    def is_zh(self, c):
        x = ord (c)
        # Punct & Radicals
        if x >= 0x2e80 and x <= 0x33ff:
            return True
        # Fullwidth Latin Characters
        elif x >= 0xff00 and x <= 0xffef:
            return True       
        # CJK Unified Ideographs &
        # CJK Unified Ideographs Extension A
        elif x >= 0x4e00 and x <= 0x9fbb:
            return True
        # CJK Compatibility Ideographs
        elif x >= 0xf900 and x <= 0xfad9:
            return True     
        # CJK Unified Ideographs Extension B
        elif x >= 0x20000 and x <= 0x2a6d6:
            return True       
        # CJK Compatibility Supplement
        elif x >= 0x2f800 and x <= 0x2fa1d:
            return True    
        else:
            return False
            
    def split_zh_en (self, zh_en_str):
        zh_en_group = []
        zh_gather = ""
        en_gather = ""
        zh_status = False
        for c in zh_en_str:
            if not zh_status and self.is_zh (c):
                zh_status = True
                if en_gather != "":
                    zh_en_group.append([mark["en"],en_gather])
                    en_gather = ""
            elif not self.is_zh (c) and zh_status:
                zh_status = False
                if zh_gather != "":
                    zh_en_group.append([mark["zh"], zh_gather])
            if zh_status:
                    zh_gather += c
            else:
                    en_gather += c                               
                    zh_gather = ""
    
        if en_gather != "":
            zh_en_group.append ([mark["en"],en_gather])
        elif zh_gather != "":
            zh_en_group.append ([mark["zh"],zh_gather])
    
        return zh_en_group

    def separateenwords(self, text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']
    
    def separatechwords(self, text):
        l = len(text)
        
        p = [0 for i in range(l + 1)]
        p[l] = 1
        div = [1 for i in range(l + 1)]
        t = [1 for i in range(l)]
        for i in range(l - 1, -1, -1):
            for k in range(1, l - i + 1):
                tmp = d[text[i:i + k]]
                if k > 1 and tmp == 1:
                    continue
                if(d[text[i:i + k]] * p[i + k] * div[i] > p[i] * d['_t_'] * div[i + k]):
                    p[i] = d[text[i:i + k]] * p[i + k]
                    div[i] = d['_t_'] * div[i + k]
                    t[i] = k
        i = 0
        words_list = []
        while i < l:
            #print text[i:i+t[i]]
            word = str(text[i:i + t[i]]) + u'' 
            #print word
            words_list.append(str(word))
            i = i + t[i]
        #print words_list
        return words_list
    
    # Return true if this url is already indexed
    def isindexed(self, url):
        pattern = '^http://api.douban.com/v2/book/(\d{7,8})/$' 
        if re.search(pattern, url):
            url = url.replace('http://api.douban.com/v2/book/', 'http://book.douban.com/subject/')
        #print "IsIndexed: %s" % url
        self.cur.execute("select id from books_urllist where url='%s'" % url)
        u = self.cur.fetchone()
        if u != None:
            self.cur.execute(
            'select * from books_wordlocation where urlid=%d' % u[0])
            v = self.cur.fetchone()
            if v != None:
                return True
        return False
    
    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo):
        pattern = '^http://api.douban.com/v2/book/(\d{7,8})/$' 
        if re.search(pattern, urlFrom):
            urlFrom = urlFrom.replace('http://api.douban.com/v2/book/', 'http://book.douban.com/subject/')
        if re.search(pattern, urlTo):
            urlTo = urlFrom.replace('http://api.douban.com/v2/book/', 'http://book.douban.com/subject/')
        fromid = self.getentryid('books_urllist', 'url', urlFrom)
        toid = self.getentryid('books_urllist', 'url', urlTo)
        self.cur.execute('insert into books_link(fromid, toid) values (%s, %s)' % (fromid, toid))
        self.dbcommit()
    
    def getlinks(self, page):
        h = httplib2.Http()
        #time.sleep(0.5)
        try:
            response, homepage = h.request(page)
        except:
            print 'Could not open %s' % page
            return
        #print homepage
        homepagetext = bytes.decode(homepage)
        #print string
        soup = BeautifulSoup(homepagetext)
                
        links = soup('a')
        pages = set()
        for link in links:
            #print link
            if ('href' in dict(link.attrs)):
                #if link['href'][0:31] == 'http://book.douban.com/subject/':
                pattern = '^http://book.douban.com/subject/(\d{7,8})/$' 
                #print re.search(pattern, 'M') 
                #print re.search('^http://book.douban.com/subject/(\d{7, 8})$', link['href'])
                #print link['href']
                if re.search(pattern, link['href']):
                    pages.add(link['href'].replace('http://book.douban.com/subject/', 'http://api.douban.com/v2/book/'))
        return pages
    
    def crawl(self, index, depth=1):
        pages = self.getlinks(index)
        
        for i in range(depth):
            newpages = set()
            for page in pages:                 
                #time.sleep(0.5)
                try:
                    response, content = h.request(page + '?apikey=053c18e01a741faf0fb44aa04f5c5f0d')
                    string = bytes.decode(content)
                    #print string
                    #root = etree.fromstring(string)
                    self.addtoindex(page, string)
                    
                    url = page.replace('http://api.douban.com/v2/book/', 'http://book.douban.com/subject/')
                    #print url
                    
                    urls = self.getlinks(url)
                    #print urls
                    for url in urls:
                        if not self.isindexed(url):
                            #print "Adding"
                            newpages.add(url)
                        #linkText = self.gettextonly(url)
                        self.addlinkref(page, url)
                except:
                    print 'Error %s' % page
                    continue
                self.dbcommit()

            #print newpages
            pages = newpages

        
    def calculatepagerank(self, iterations=20):
        #self.cur.execute('drop table if exists pagerank')
        #self.cur.execute('create table pagerank(urlid INT NOT NULL, score FLOAT NOT NULL, primary_key, urlid)')
        
        self.cur.execute('insert into books_pagerank(urlid,score) select id, 1.0 from books_urllist')
        self.dbcommit()
        
        for i in range(iterations):
            print "Iteration %d" % (i)
            self.cur.execute('select id from books_urllist')
            rowids = self.cur.fetchall()
            for (urlid,) in rowids:
                pr = 0.15
                self.cur.execute('select distinct fromid from books_link where toid=%d' % urlid)
                fromids = self.cur.fetchall()
                for(linker,) in fromids:
                    self.cur.execute(
                    'select score from books_pagerank where urlid=%d' % linker)
                    linkingpr = self.cur.fetchone()[0]
                    
                    self.cur.execute(
                    'select count(*) from books_link where fromid=%d' % linker)
                    linkingcount = self.cur.fetchone()[0]
                    pr += 0.85 * (linkingpr / linkingcount)
                    #print 'result is %f' % (linker/linkingcount)
                self.cur.execute(
                    'update books_pagerank set score=%f where urlid=%d' % (pr, urlid))
            self.dbcommit()
            
    def changepicpath(self, target):
        self.cur.execute('select id, pic from books_book')
        urls = dict(self.cur.fetchall())
        #print urls
        for id in urls.keys():
            #print id
            newpath = urls[id].replace('/home/hehe/eclipse/workspace/douban/DoubanImages/', target)
            print newpath
            self.cur.execute("update books_book set pic='%s' where id=%d" % (newpath, id))
        self.dbcommit()
        
#crawler = crawler('localhost', 'root', '1234', 'douban')
#index = 'http://book.douban.com/tag/%E6%97%85%E8%A1%8C'
#crawler.crawl(index)
#crawler.updatebook_intro()
#crawler.changepicpath('/static/')
