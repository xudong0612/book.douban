# -*- coding: UTF-8 -*-
import MySQLdb
from math import sqrt
from math import log
class Recommendation:
    def __init__(self, host, user, psw, dbname):
        self.con = MySQLdb.connect(host, user, psw, dbname, charset='utf8')
        self.cur = self.con.cursor()
        self.prefs = dict()
        
    def getRatingsByUserID(self, userid):
        self.cur.execute('select book_id, score from books_evaluation where user_id=%d' % userid)
        rating = self.cur.fetchall()
        #print rating
        ratings = dict([(row[0], row[1]) for row in rating])
        #print ratings
        self.prefs[userid] = ratings
        
    def printmatrix(self):
        print self.prefs
    
    def sim_pearson(self, prefs, p1, p2):
        #print 'aaaa'
        si = {}
        for item in prefs[p1]:
            if item in prefs[p2]: 
                si[item] = 1
        
        n = len(si)
        
        if n == 0:
            return 0
        
        sum1 = sum([prefs[p1][it] for it in si])
        sum2 = sum([prefs[p2][it] for it in si])
        
        sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
        sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])
        
        pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])
        
        num = pSum - (sum1 * sum2 / n)
        
        den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
        
        if den == 0:
            return 0
        
        r = num / den
        return r

    def topMatches(self, prefs, person, n=5, similarity=sim_pearson):
        scores = [(similarity(prefs, person, other), other) 
                  for other in prefs if other != person]
        scores.sort()
        scores.reverse()
        return scores[0:n]

    def transformPrefs(self):
        result = {}
        for person in self.prefs:
            for item in self.prefs[person]:
                result.setdefault(item, {})
                result[item][person] = self.prefs[person][item]
        return result
    
    def sim_distance(self, prefs, person1, person2):
        si = {}
        for item in prefs[person1]:
            if item in prefs[person2]:
                si[item] = 1.0
        
        if len(si) == 0:
            return 0
        
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
                              for item in prefs[person1] if item in prefs[person2]])
        return 1 / (1.0 + sum_of_squares)

    def calculateSimilarItems(self, n=10):
        result = {}
        itemPrefs = self.transformPrefs()
        #print itemPrefs
        c = 0.0
        for item in itemPrefs:
            c += 1
            if c % 100 == 0:
                print "%d / %d" % (c, len(itemPrefs))
            scores = self.topMatches(itemPrefs, item, n=n, similarity=self.sim_distance)
            result[item] = scores
        return result
    
    #print itemsim
    '''def getRecommendationItems(self, itemMatch, user):
        #print prefs
        userRatings = self.prefs[user]
        #print userRatings
        scores = {}
        totalSim = {}
        for (item, rating) in userRatings.items():
            for (similarity, item2) in itemMatch[item]:
                if item2 in userRatings:
                    continue
                scores.setdefault(item2, 0.0)
                scores[item2] += similarity * rating
                totalSim.setdefault(item2, 0.0)
                totalSim[item2] += similarity
        rankings = [(score / (totalSim[item] + 1.0), item) for item, score in scores.items()]
        rankings.sort()
        rankings.reverse()
        return rankings'''
    
    def getPopularTagByUser(self, userid):
        self.cur.execute('SELECT user_id, book_id, tag_id FROM books_tagging')
        
        tags = self.cur.fetchall()
        records = []
        for i in range(len(tags)):
            records.append(tags[i])
        print records
        user_tags = dict()
        tag_items = dict()
        user_items = dict()
        for user, item, tag in records:
            print user, item, tag
            if not user_tags.has_key((user, tag)):
                user_tags[user, tag] = 1
            else:
                user_tags[user, tag] += 1
            if not tag_items.has_key((tag, item)):
                tag_items[tag, item] = 1
            else:
                tag_items[tag, item] += 1
            if not user_items.has_key((user, item)):
                user_items[user, item] = 1
            else:
                user_items[user, item] += 1
        print tag_items[4]
        
    def RecommendThroughTags(self, userid):
        recommend_items = dict()
        self.cur.execute('SELECT book_id FROM books_tagging where user_id=%d' % userid)
        result = self.cur.fetchall()
        tagged_items = []
        for i in range(len(result)):
            tagged_items.append(result[i][0])
        #print tagged_items
        self.cur.execute('SELECT tag_id, count(*) FROM books_tagging where user_id = %d group by tag_id' % userid)
        result = self.cur.fetchall()
        user_tags = dict()
        for tag, count in result:
            user_tags[tag] = count
        #print user_tags
        for tag, wut in user_tags.items():
            #print tag, wut
            self.cur.execute('SELECT book_id, count(*) FROM books_tagging where tag_id = %d group by book_id' % tag)
            results = self.cur.fetchall()
            #print results
            tag_items = dict()
            for item, count in results:
                tag_items[item] = count
            #print tag_items
            self.cur.execute('SELECT count(distinct(user_id)) FROM books_tagging where tag_id = %d' % tag)
            result = self.cur.fetchall()
            tagCount = result[0][0]
            #print count
            for item, wui in tag_items.items():
                self.cur.execute('select count(distinct(user_id)) FROM books_tagging where book_id=%d' % item)
                result = self.cur.fetchall()
                userCount = result[0][0]
                if item in tagged_items:
                    #print 'in'
                    continue
                if item not in recommend_items:
                    recommend_items[item] = wut * wui / (log(1 + float(tagCount)) * log(1 + float(userCount)))
                else:
                    recommend_items[item] += wut * wui / (log(1 + float(tagCount)) * log(1 + float(userCount)))
        #print 'recommend', recommend_items   
        return recommend_items
    
    def RecommendUserByTags(self, user_id):
        recommend_users = dict()
        self.cur.execute('SELECT distinct(tag_id) FROM books_tagging where user_id=%d' % user_id)
        result = self.cur.fetchall()
        user_tags = []
        for i in range(len(result)):
            user_tags.append(result[i][0])
        #print user_tags
        for tagid in user_tags:
            self.cur.execute('SELECT distinct(user_id) FROM books_tagging where tag_id=%d' % tagid)
            userids = self.cur.fetchall()
            for userid in userids:
                if userid[0] != user_id:
                    if recommend_users.has_key(userid[0]):
                        recommend_users[userid[0]] += 1
                    else:
                        recommend_users[userid[0]] = 1
                        
        print recommend_users
        
    def UserSimilarity(self, userid):
        item_users = dict()
        self.cur.execute("SELECT distinct(book_id) FROM books_evaluation")
        result = self.cur.fetchall()
        for i in range(len(result)):
            if result[i][0] not in item_users:
                item_users[result[i][0]] = set()
            self.cur.execute("SELECT user_id FROM books_evaluation where book_id=%d" % result[i][0])
            userids = self.cur.fetchall()
            for j in range(len(userids)):
                item_users[result[i][0]].add(userids[j][0])
        
        C = {}
        N = dict()
        for i, users in item_users.items():
            for u in users:
                if C.has_key(u):
                    subdict = C[u]
                else:
                    subdict = {}
                if not N.has_key(u):
                    N[u] = 1
                else:
                    N[u] += 1
                for v in users:
                    if u == v:
                        continue          
                    C[u] = subdict
                    if not subdict.has_key(v):
                        subdict[v] = 1 / log(1 + len(users))
                    else:
                        subdict[v] += 1 / log(1 + len(users))
        W = {}
        for u, related_users in C.items():
            if W.has_key(u):
                    subdict = W[u]
            else:
                    subdict = {}
            for v, cuv in related_users.items():
                W[u] = subdict
                subdict[v] = cuv / sqrt(N[u] * N[v])
        #print W
        return W[userid]
    
    def getRecommendationItems(self, user):
        self.cur.execute('select id from books_user')
        users = self.cur.fetchall()
        for userid in users:
            #print userid[0] 
            self.cur.execute('select book_id, score from books_evaluation where user_id=%d' % userid[0])
            rating = self.cur.fetchall()
            #print rating
            ratings = dict([(row[0], row[1]) for row in rating])
            #print ratings
            self.prefs[userid[0]] = ratings
        
        
        result = {}
        itemPrefs = self.transformPrefs()
        #print itemPrefs
        c = 0.0
        for item in itemPrefs:
            c += 1
            if c % 100 == 0:
                print "%d / %d" % (c, len(itemPrefs))
            scores = self.topMatches(itemPrefs, item, n=10, similarity=self.sim_distance)
            result[item] = scores       
        #print result
        #print prefs
        userRatings = self.prefs[user]
        #print userRatings
        scores = {}
        totalSim = {}
        for (item, rating) in userRatings.items():
            for (similarity, item2) in result[item]:
                if item2 in userRatings:
                    continue
                scores.setdefault(item2, 0.0)
                scores[item2] += similarity * rating
                totalSim.setdefault(item2, 0.0)
                totalSim[item2] += similarity
        rankings = [(score / (totalSim[item] + 1.0), item) for item, score in scores.items()]
        rankings.sort()
        rankings.reverse()
        return rankings
                    
            
        
#r = Recommendation('localhost', 'root', '1234', 'douban')
#r.RecommendUserByTags(1)
#r.getRatingsByUserID(1)
#r.getRatingsByUserID(2)
#r.getRatingsByUserID(3)
#r.getRatingsByUserID(4)
#r.getRatingsByUserID(6)
#r.printmatrix()

#itemsim = r.calculateSimilarItems()
#print itemsim
#print r.getRecommendationItems(itemsim, 1)

#r.RecommendThroughTags(1)
#print r.UserSimilarity(1)
