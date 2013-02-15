# -*- coding: UTF-8 -*-
'''
Created on 2012-12-19

@author: edward
'''

from douban.books.models import *

def latestBooks():
    return Book.objects.all().order_by('-publication_date')[0:10]

def popularBooks():
    return Book.objects.all().order_by('-evaluation')[0:10]

def popularComments():
    return Comment.objects.all().order_by('-rate')[0:10]

#TODO
def recommandedBooks():
    return 

def counts(self,tag):
    tagging = Tagging.objects.filter(tag=tag)
    return len(tagging)

def popularTag(type):
    tags = Tag.objects.filter(type=type)
    sorted(tags,counts)
    return tags[0:7]
    