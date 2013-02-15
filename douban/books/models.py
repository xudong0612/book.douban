# -*- coding: UTF-8 -*- 

from django.db import models
from django.db.models.fields import CharField
from django.contrib.localflavor.generic.forms import DateField

# Create your models here.

class Type(models.Model):
    type = models.CharField(max_length=100)

class Tag(models.Model):
    contents = models.CharField(max_length=100)
    type = models.ForeignKey(Type)
    
    def _unicode_(self):
        return u'contents:%s' % self.contents
    

class User(models.Model): 
    email = models.EmailField()
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=14)
    pic = models.CharField(max_length=1024,null=True)
    
    def _unicode_(self):
        return u'email:%s,username:%s,password:%s' % (self.email, self.username, self.password)
    
class watch(models.Model):
    watcher = models.ForeignKey(User, related_name = 'watch_watcher')
    watching = models.ForeignKey(User, related_name = 'watch_watching')
    


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=100)
    publication = models.CharField(max_length=100)
    publication_date = models.DateField(null=True)
    evaluation = models.DecimalField(max_digits=3,decimal_places=1)
    pic = models.CharField(max_length=200)
    content_profile = models.TextField(null=True)
    author_profile = models.TextField(null=True)
    catalog = models.TextField(null=True)
    pages = models.IntegerField()
    price = models.CharField(max_length=20)
    isbn = models.CharField(max_length=20)
    urlid = models.IntegerField()
    type = models.ForeignKey(Type)
    
    def _unicode_(self):
        return u'title:%s,author:%s,publication:%s,publication date:%s,content profile:%s,author profile:%s,catalog:%s,pages:%s,price:%s,isbn:%s,comments:%s,notes:%s' % (self.title,self.author,self.publication,self.publication_date,self.content_profile,self.author_profile,self.catalog,self.pages,self.price,self.isbn,self.comments,self.notes)
    
class List(models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    status = models.CharField(max_length=4)
    contents = models.TextField()
    date = models.DateField()
    
class evaluation(models.Model):
    score = models.IntegerField()
    book = models.ForeignKey(Book,related_name='evaluatioins')
    user = models.ForeignKey(User)
    
class Note(models.Model):
    contents = models.TextField()
    date = models.DateField()
    evaluateion = models.IntegerField()
    user = models.ForeignKey(User,related_name='note_own')
    book = models.ForeignKey(Book)
    page = models.IntegerField()
    paragraph = models.CharField(max_length=100)
    privilege = models.IntegerField()
    collectors = models.ManyToManyField(User,related_name='note_collection')
    
    def _unicode_(self):
        return u'evaluation:%s,contents:%s,date:%s.user:%s,page:%s,paragragh:%s,privilege:%s,replies:%s' % (self.evaluateion, self.contents, self.date, self.user, self.page, self.paragraph, self.privilege, self.replies)

class Comment(models.Model):
    title = models.CharField(max_length=200)
    evaluateion = models.IntegerField()
    contents = models.TextField()
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)
    date = models.DateField()
    rate = models.IntegerField()
    derate = models.IntegerField()
    
    def _unicode_(self):
        return u'title:%s.evaluation:%s,contents:%s,user:%s,date:%s' % (self.title, self.evaluation, self.contents, self.user, self.date)
 
class Reply(models.Model):
    date = models.DateField()
    user = models.ForeignKey(User)
    cotents = models.TextField()
    note = models.ForeignKey(Note,null=True)
    commmet = models.ForeignKey(Comment,null=True)
    
    def _unicode_(self):
        return u'date:%s,user:%s,contents:%s' % (self.date, self.user, self.cotents)   
    
class Recommandation(models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book,null=True)
    note = models.ForeignKey(Note,null=True)
    date = models.DateField()
    
class Tagging(models.Model):
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey(User)
    book = models.ForeignKey(Book)

    


    

    

    
    
    
    
