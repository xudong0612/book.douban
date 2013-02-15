# -*- coding: UTF-8 -*-
import httplib2
import json
import MySQLdb
import xml.etree.ElementTree as etree
from bs4 import BeautifulSoup
from urlparse import urljoin
import re
import collections
import time
d = collections.defaultdict(lambda:1)
ignorewords = set(['?', '、', '。', '“', '《', '》', '”', '！', '(', ')', '[', ']','？', '，', '（', '）', '*', '.'])
h = httplib2.Http()
mark = {"en":1, "zh":2}
class searcher:
    def __init__(self, host, user, psw, dbname, filename='/home/hehe/eclipse/workspace/douban/douban/books/lib/SogouLabDic.dic'):
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
    
    def getmatchrows(self, q):
        urlscore = dict()
        #print q
        query="select urlid from books_book where title='" + q + "'"
        self.cur.execute(query)
        urlrows = self.cur.fetchall()
        #print urlrows
        if urlrows != None:
            for url in urlrows:
                #print "Equal: %s" % url
                urlscore[url] = 5              
        #words = self.separatewords(q.decode('utf8'))
        
        zh_en_group=self.split_zh_en(q.decode('utf8'))
        #print urlid
        words_list = []
        for st in zh_en_group:
            if st[0] == mark["en"]:
                words = self.separateenwords(st[1] + u'')
                for i in range(len(words)):
                    words_list.append(words[i])
            else:
                words = self.separatechwords(st[1].strip().decode('utf8'))
                for i in range(len(words)):
                    words_list.append(words[i])
        #print words_list       
        for word in words_list:       
            query="select urlid from books_wordlocation inner join books_wordlist on books_wordlist.id=books_wordlocation.wordid where books_wordlist.isexactly=0 and books_wordlist.word='" + word+"'"
            #print query
            self.cur.execute(query)
            urlrows = self.cur.fetchall()
            #print word, urlrows
            
            if urlrows != None:
                for url in urlrows:
                    if  not urlscore.has_key(url):
                        urlscore[url] = 0
                    else:
                        urlscore[url] += 2
                        
            query="select urlid from books_wordlocation inner join books_wordlist on books_wordlist.id=books_wordlocation.wordid where books_wordlist.isexactly=0 and books_wordlist.word like '%" \
                + word +"%' and books_wordlist.word !='" + word + "'"
            #print query
            self.cur.execute(query)
            urlrows = self.cur.fetchall()
            #print word, urlrows
            
            if urlrows != None:
                for url in urlrows:
                    if  not urlscore.has_key(url):
                        urlscore[url] = 0
                    else:
                        urlscore[url] += 1
                        
            query="select urlid from books_wordlocation inner join books_wordlist on books_wordlist.id=books_wordlocation.wordid where INSTR('" + word + "', books_wordlist.word)>0"
            #print query
            self.cur.execute(query)
            urlrows = self.cur.fetchall()
            #print word, urlrows
            
            if urlrows != None:
                for url in urlrows:
                    if  not urlscore.has_key(url):
                        urlscore[url] = 0
                    else:
                        urlscore[url] += 0.5
        #print urlscore
        return urlscore
    
    def getscoredlist(self, rows):
        totalscores=dict()
        #print totalscores
        
        weights = [(1.0, self.frequencyscore(rows.keys())),
                  (1.0, self.locationscore(rows.keys())),
                  (1.0, self.pagerankscore(rows.keys()))]
                  #(1.0, self.ratingscore(rows.keys()))]
        
        for (k, v) in rows.items():
            #print "dict[%s] =" % k, v
            totalscores[k] = v
        for (weight, scores) in weights:
            #print scores[15354]
            for url in totalscores.keys():
                #print url
                totalscores[url] += weight * scores[url[0]]
        #print totalscores
        return totalscores
    
    def geturlname(self, id):
        self.cur.execute(
            "select title from books_book where urlid=%d" % id)
        title = self.cur.fetchone()[0] + u''
        #print title
        self.cur.execute(
            "select author from books_book where urlid=%d" % id)
        author = self.cur.fetchone()[0] + u''
        self.cur.execute(
            "select evaluation from books_book where urlid=%d" % id)
        rating = self.cur.fetchone()[0] + u''
        #print author
        return title + ' ' + author + ' ' + rating
    
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
           
    def query(self, q):      
        urlids = self.getmatchrows(q)
        #print urlids
        if len(urlids) == 0:
            #print 'No result...'
            return
        scores = self.getscoredlist(urlids)
        rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
        #results = dict()
        #for (score, urlid) in rankedscores[0:25]:
            #print self.geturlname(urlid), score
        #    results[urlid] = self.getbookinfobyurlid(urlid)
        #return wordids, [r[1] for r in rankedscores[0:10]]
        return rankedscores
    
    def getbookinfobyurlid(self, urlid):
        #book = dict()
        self.cur.execute('select title, author, publication, publication_date, price from books_book where urlid=%d' % urlid)
        bookinfo = self.cur.fetchone()
        title = bookinfo[0] + u''
        author = bookinfo[1] + u''
        publication = bookinfo[2] + u''
        pubdate = str(bookinfo[3])
        price = str(bookinfo[4])
        return title + ':' + author + '/' + publication + '/' +  pubdate + '/' + price
        
    def normalizesscores(self, scores, smallIsBetter=0):
        vsmall = 0.00001
        if smallIsBetter:
            minscore = min(scores.values())
            return dict([(u, float(minscore) / max(vsmall, l)) for (u, l) \
                         in scores.items()])
        else:
            maxscore = max(scores.values())
            if maxscore == 0:
                maxscore = vsmall
            return dict([(u, float(c) / maxscore) for (u, c) in scores.items()])
        
    def frequencyscore(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:
            counts[row[0]] += 1
        return self.normalizesscores(counts)
      
    def locationscore(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            #print loc
            if loc < locations[row[0]]:
                locations[row[0]] = loc
        return self.normalizesscores(locations, smallIsBetter=1)
    
    def ratingscore(self, rows):
        ratings = dict()
        for row in rows:
            self.cur.execute("select evaluation from books_book where urlid=%s" % row)
            rating = str(self.cur.fetchone()[0])
            ratings[row[0]] = float(rating)
        return self.normalizesscores(ratings)
    
    def distancescore(self, rows):
        if len(rows[0]) <= 2:
            return dict([(rows[0], 1.0) for row in rows])
        mindistance = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < mindistance[row[0]]:
                mindistance[row[0]] = dist
        return self.normalizesscores(mindistance, smallIsBetter=1)
    
    def pagerankscore(self, rows):
        for row in rows:
            pageranks = dict([(row[0], 0)])
        for row in rows:
            self.cur.execute("select score from books_pagerank where urlid=%d" % row[0])
            pageranks[(row[0])] = self.cur.fetchone()[0]
        maxrank = max(pageranks.values())
        normalizedscores = dict([(u, float(1) / maxrank) for (u, l) in pageranks.items()])
        return normalizedscores
    
    def linktextscore(self, rows, wordids):
        linkscores = dict([(row[0], 0) for row in rows])
        for wordid in wordids:
            self.cur.execute('select books_link.fromid, books_link.toid from books_linkwords, books_link where \
            wordid=%d and books_linkwords.linkid=books_link.rowid' % wordid)
            result = self.cur.fetchall()
            #print len(result)
            for (fromid, toid) in result:
                if toid in linkscores:
                    self.cur.execute('select score from books_pagerank where urlid=%d' % toid)
                    pr = self.cur.fetchone()[0]
                    linkscores[toid] += pr
        maxscore = max(linkscores.values())
        normalizedscores = dict([(u, float(1) / maxscore) for (u, l) in linkscores.items()])
        return normalizedscores

#e=searcher('localhost', 'root', '1234', 'douban')
#e.query('看见')