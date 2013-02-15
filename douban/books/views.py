# -*- coding: UTF-8 -*-
# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from douban.books.util import *
from douban.books.forms import *
from douban.books.constant import *
import datetime
from urllib2 import HTTPRedirectHandler
from django.shortcuts import render_to_response, render
import logging
from douban.books.lib.SearchBook import *
from douban.books.lib.Recommend import *
# Get an instance of a logger
logger = logging.getLogger(__name__)


# /account
def account(request):
    extra = {}
    logger.info("invoke account")
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        form = accountForm(initial={'username':user.username})
        if request.method == 'POST':
            form = accountForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user.username = cd['username']
                user.save()
        logger.info("invoke account")
        extra['form'] = form
        return render_to_response('account.tml',extra)
    else:
        extra['user'] = -1
        return render_to_response('error.tml',extra)

# /account/login
def login(request):
    # if success redirect to / or back to /account/login
    extra = {}
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1
    form = loginForm()
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.filter(email = cd['email'])
            if not user:
                #error email and password are not matched and back to this page with error info 
                form.errors['email'] = [u'用户名密码不正确']
                extra['form'] = form
                return render_to_response('login.tml',extra)
            else:
                if user[0].password == cd['password']:
                    request.session['userid'] = user[0].id
                    return HttpResponseRedirect('/')
                else:
                    #error email and password are not matched and back to this page with error info 
                    form.errors['email'] = [u'用户名密码不正确']
                    extra['form'] = form
                    return render_to_response('login.tml',extra)
        else:
            #form is not valid and back to this page with error info 
            extra['form'] = form
            return render_to_response('login.tml',extra)
    extra['form'] = form
    return render_to_response('login.tml',extra)    

# /
def splesh(request):
    latestbooks = latestBooks()
    popularbooks = popularBooks()
    popularcomments = popularComments()
    rec = Recommendation('localhost', 'root', 'hehe', 'douban')
    
    extra = {}
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        
        logger.info(user.username)
        recommand = rec.getRecommendationItems(user.id)
        recommendations = []
        #print recommand
        for key in recommand:
            recommendations.append(Book.objects.filter(id=key[1])[0])
        extra['recommendations'] = recommendations[0:8]
    else:
        extra['user'] = -1
    extra['latests'] = latestbooks
    extra['populars'] = popularbooks
    extra['comments'] = popularcomments
    logger.info(popularcomments)
    types = Type.objects.all()
    tagclasses = [[]]
    for type in types:
        tagclasses.append(popularTag(type))
    logger.info(latestbooks)
    extra['tagclasses'] = tagclasses
    return render_to_response('splesh.tml',extra)

# /account/register
def register(request):
    # if success return success page or failed page
    extra = {}
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1  
    if request.method == 'POST':
        form = registerForm(request.POST)
        if(form.is_valid()):
            cd = form.cleaned_data
            user = User.objects.filter(email = cd['email'])
            if user:
                #email is already registered
                form = registerForm()
                form.errors['email'] = [u'邮箱已经注册过']
                logger.info('already register')
                extra['form'] = form
                return render_to_response('register.tml',extra)
            elif len(cd['password']) < 6:
                form = registerForm()
                form.errors['password'] = [u'密码至少要有6位']
                logger.info(u'密码至少要有6位')
                extra['form'] = form
                return render_to_response('register.tml',extra)
            elif len(cd['password']) > 16:
                form = registerForm()
                form.errors['password'] = [u'密码至多有16位']
                logger.info(u'密码至多有16位')
                extra['form'] = form
                return render_to_response('register.tml',extra)
            else:
                user = User(email=cd['email'],username=cd['username'],password=cd['password'])
                user.save()
                logger.info('valid and save')
                user = User.objects.filter(email=user.email)
                request.session['userid'] = user[0].id
                return HttpResponseRedirect('/')
        else:
            #register info is not valid and back to this page with error info 
            logger.info('invalid')
            logger.info(form.errors)
            extra['form'] = form
            return render_to_response('register.tml',extra)
    else:
        form = registerForm()
        logger.warning(form.as_table())
        extra['form'] = form
     
    return render_to_response('register.tml',extra)

# /account/logout
def logout(request):
    # logout and redirect to /account/login
    del request.session['userid']
    return HttpResponseRedirect('/account/login')

def book(request,bookid):
    extra = {}
    book = Book.objects.filter(id=bookid)[0]
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        list = List.objects.filter(user = user,book = book)
        if len(list) > 0:
            extra['status'] = list[0].status
        else:
            extra['status'] = -1
        rec = Recommandation.objects.filter(user = user,book = book)
        if len(rec) > 0:
            extra['recommandation'] = 0
        else:
            extra['recommandation'] = 1
    else:
        extra['user'] = -1 
        extra['status'] = -1 
        extra['recommandation'] = 0
    notes = book.note_set.all()
    comments = book.comment_set.all()
    lists = List.objects.filter(book=book)
    users = []
    for list in lists:
        users.append(list.user)
    
    extra['book'] = book
    extra['notes'] = notes
    extra['comments'] = comments
    extra['users'] = users
    return render_to_response('book.tml',extra)

def sharebook(request,bookid):
    extra = {}
    book = Book.objects.filter(id=bookid)[0]
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        list = List.objects.filter(user=user, book=book)
    else:
        extra['user'] = -1
        list = []
        return render_to_response('error.tml',extra)
    
    extra['book'] = book
    form = sharebookForm()
    initial = {}
    if len(list) > 0:
        initial['status']=list[0].status
    eval = evaluation.objects.filter(user=user, book=book)
    if len(eval) > 0:
        initial['evaluate']=EVA_CHOICE[eval[0].score/2 - 1][0]
    form = sharebookForm(initial = initial)
    if request.method =='POST':
        form = sharebookForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            list = List.objects.filter(user = user,book = book)
            if len(list) > 0:
                list = list[0]
                list.status = cd['status']
                list.contents = cd['contents']
                list.save()
            else:
                list = List(status = cd['status'],user = user,book = book,contents = cd['contents'],date=datetime.datetime.now())
                list.save()
            eval = evaluation.objects.filter(user = user,book = book)
            if len(eval) > 0:
                evaluate = eval[0]
                evaluate.score = cd['evaluate']
                evaluate.save()
            else:
                eval = evaluation(score = cd['evaluate'],user = user,book = book)
                eval.save()
            evals = evaluation.objects.filter(book = book)
            sum = 0
            for e in evals:
                sum = sum + e.score
            eval = sum / len(evals)
            book.evaluation = eval
            book.save()
            stags = cd['tags']
            tags = stags.split(' ')
            for tag in tags:
                tag_temp = Tag.objects.filter(contents = tag)
                if len(tag_temp) == 0:
                    tag_temp = Tag(contents = tag,type = book.type)
                    tag_temp.save()
                else:
                    tag_org = tag_temp[0]
                    tag_temp = tag_org
                tagging = Tagging(tag = tag_temp,user = user,book = book)
                tagging.save()
            return HttpResponseRedirect('%s%d' % ('/book/',book.id))
        else:
            extra['form'] = form
            return render_to_response('sharebook.tml',extra)
    extra['form'] = form
    types = Type.objects.all()
    tagclasses = [[]]
    for type in types:
        tagclasses.append(popularTag(type))
    extra['tagclasses'] = tagclasses
    tags_temp = Tagging.objects.filter(user = user,book = book).values('tag').distinct()
    tags = []
    for var in tags_temp:
        tags.append(Tag.objects.filter(id=var['tag'])[0])
    extra['mytags'] = tags[0:7]
    return render_to_response('sharebook.tml',extra)

def mine(request):
    extra = {}
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
         
    else:
        extra['user'] = -1  
        return render_to_response('error.tml',extra)
    reading = List.objects.filter(user=user, status=u'在读')
    toread = List.objects.filter(user=user, status=u'想读')
    readed = List.objects.filter(user=user, status=u'读过')
    notes_own = user.note_own.all()
    notes_collection = user.note_collection.all()
    comments = user.comment_set.all()
    extra['reading'] = reading
    extra['toread'] = toread
    extra['readed'] = readed
    extra['notes_own'] = notes_own
    extra['notes_collection'] = notes_collection
    extra['comments'] = comments
    rec = Recommandation.objects.filter(user = extra['user'])
    extra['recs'] = rec
    return render_to_response('mine.tml', extra)

def user(request,userid):
    touser = User.objects.filter(id = userid)[0]
    
    extra = {}
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if touser == user:
            return HttpResponseRedirect('/mine')
    else:
        extra['user'] = -1  
    extra['touser'] = touser
    reading = List.objects.filter(user=touser, status=u'在读')
    toread = List.objects.filter(user=touser, status=u'想读')
    readed = List.objects.filter(user=touser, status=u'读过')
    notes_own = touser.note_own.filter(privilege=1)
    notes_collection = touser.note_collection.all()
    comments = touser.comment_set.all()
    extra['reading'] = reading
    extra['toread'] = toread
    extra['readed'] = readed
    extra['notes_own'] = notes_own
    extra['notes_collection'] = notes_collection
    extra['comments'] = comments
    recomandationbooks = Recommandation.objects.filter(user = touser).values('book')
    recbooks = []
    for var in recomandationbooks:
        recbooks.append(Book.objects.filter(id=var['book'])[0])
    extra['recbooks'] = recbooks
   
    return render_to_response('user.tml', extra)
            
def movement(request):    
    extra = {}    
    if 'userid' in request.session:        
        userid = request.session['userid']        
        u = User.objects.filter(id=userid)[0] 
        extra['user'] = u       
        books = List.objects.filter(user = u)        
        extra['books'] = books        
        return render_to_response('movement.tml',extra)    
    else:        
        extra['user'] = -1
        return render_to_response('error.tml',extra)
    
    
def user_comments(request,userid):
    extra = {}
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if user.id == userid:
            extra['mine'] = 1
        else:
            extra['mine'] = 0
    else:
        extra['user'] = -1 
        extra['mine'] = 0
    touser = User.objects.filter(id=userid)[0]
    extra['touser'] = touser
    comments = touser.comment_set.all()
    extra['comments'] = comments
    return render_to_response('user_comments.tml',extra)

def user_notes(request,userid):
    extra = {}
    touser = User.objects.filter(id=userid)[0]
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if user == touser:
            extra['mine'] = 1
            notes = touser.note_own.all()
            extra['notes'] = notes
            logger.info(notes)
        else:
            extra['mine'] = 0
            notes = touser.note_own.filter(privilege=1)
            extra['notes'] = notes
    else:
        extra['user'] = -1 
        extra['mine'] = 0
        notes = touser.note_own.filter(privilege=1)
        extra['notes'] = notes
    extra['touser'] = touser
   
    return render_to_response('user_notes.tml',extra)

def recommandations(request,bookid):
    extra = {}
    book = Book.objects.filter(id=bookid)[0]
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        recos = Recommandation.objects.filter(user=user)
        
        add = True
        for var in recos:
            if book == var.book:
                add = False
        if add:
            rec = Recommandation(user = user,book = book,date = datetime.datetime.now())
            rec.save()
    else:
        extra['user'] = -1  
    return HttpResponseRedirect('%s%d' % ('/book/',book.id))

def comment(request,commentid):
    comment = Comment.objects.filter(id=commentid)[0]
    form = replyForm()
    extra = {}
    book = comment.book
    extra['form'] = form
    extra['comment'] = comment
    extra['book'] = book
    comments = Comment.objects.filter(user = comment.user,book=book)
    extra['user_comments_for_book'] = comments
    comments = Comment.objects.filter(user = comment.user)
    extra['user_comments'] = comments
    list = List.objects.filter(user = comment.user,book = book)[0]
    extra['list'] = list
    replies = Reply.objects.filter(commmet=comment)
    if len(replies) > 0:
        extra['replies']  = replies
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1  
    replies = comment.reply_set
    if request.method == 'POST':
        form = replyForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(id = request.session['userid'])[0]
            cd = form.cleaned_data
            reply = Reply(date=datetime.datetime.now(),user = user,cotents = cd['contents'],commmet = comment)
            reply.save();
            #refresh this page
            return HttpResponseRedirect('%s%d' % ('/comment/' , comment.id))
        else:
            #content is null
            extra['form'] = form
            return render_to_response('comment.tml',extra)
       
    return render_to_response('comment.tml',extra)

def note(request,noteid):
    note = Note.objects.filter(id=noteid)[0]
    form = replyForm()
    extra = {}
    book = note.book
    extra['form'] = form
    extra['note'] = note
    extra['book'] = book
    
    list = List.objects.filter(user = note.user,book = book)[0]
    extra['list'] = list
    replies = Reply.objects.filter(note = note)
    if len(replies) > 0:
        extra['replies']  = replies
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if user.id == note.user.id:
            notes = Note.objects.filter(user = note.user,book=book)
            extra['user_notes_for_book'] = notes
            notes = Note.objects.filter(user = note.user)
            extra['user_notes'] = notes
        else:
            notes = Note.objects.filter(user = note.user,book=book,privilege=1)
            extra['user_notes_for_book'] = notes
            notes = Note.objects.filter(user = note.user,privilege=1)
            extra['user_notes'] = notes
    else:
        extra['user'] = -1 
        notes = Note.objects.filter(user = note.user,book=book,privilege=1)
        extra['user_notes_for_book'] = notes
        notes = Note.objects.filter(user = note.user,privilege=1)
        extra['user_notes'] = notes
    replies = note.reply_set
    if request.method == 'POST':
        form = replyForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(id = request.session['userid'])[0]
            cd = form.cleaned_data
            reply = Reply(date=datetime.datetime.now(),user = user,cotents = cd['contents'],note = note)
            reply.save();
            #refresh this page
            return HttpResponseRedirect('%s%d' % ('/note/' , note.id))
        else:
            #content is null
            extra['form'] = form
            return render_to_response('note.tml',extra)
       
    return render_to_response('note.tml',extra)

def tags(request):
    extra = {}
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1 
    form = tagForm() 
    types = Type.objects.all()
    tagclasses = {}
    for type in types:
        tagclasses[type.type] = popularTag(type)
    extra['tagclasses'] = tagclasses
    if request.method == 'POST':
        form = tagForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            tagkey = cd['tagkey']
            tag = Tag.objects.filter(contents=tagkey)
            if len(tag) > 0:
                return HttpResponseRedirect('%s%d' % ('/tag/',tag[0].id))
            else:
                form.errors['tagkey'] = [u'标签不存在']
        extra['form'] = form
        return render_to_response('tags.tml',extra)
    extra['form'] = form   
    return render_to_response('tags.tml',extra)

def tag(request,tagid):
    extra = {}
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1 
    form = tagForm()
    tag = Tag.objects.filter(id=tagid)[0]
    books_temp = Tagging.objects.filter(tag=tag).values('book').distinct()
    logger.info(tag)
    books = []
    for var in books_temp:
        books.append(Book.objects.filter(id = var['book'])[0])
    
    extra['user'] = user
    extra['tag'] = tag
    extra['books'] = books
    tags = Tag.objects.filter(type=tag.type)[0:7]
    extra['tags'] = tags
    if request.method == 'POST':
        form = tagForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            tagkey = cd['tagkey']
            tag = Tag.objects.filter(contents=tagkey)
            if len(tag) > 0:
                return HttpResponseRedirect('%s%d' % ('/tag/',tag[0].id))
            else:
                form.errors['tagkey'] = [u'标签不存在']
        extra['form'] = form
        return render_to_response('tag.tml',extra)
    extra['form'] = form  
    return render_to_response('tag.tml',extra)

def search(request):
    extra = {}
    if 'search_text' in request.GET and request.GET['search_text']:
        #搜索
        query = str(request.GET['search_text'])
        e=searcher('localhost', 'root', 'hehe', 'douban')
        print query
        results = e.query(query)
        extra = {}
        if results == None:
            print 'empty'
            return render_to_response('booklist.tml',extra)
        books = list()
        for (score, url) in results:
            #print score, url[0]
            books.append(Book.objects.filter(urlid=url[0])[0])
        extra['search'] = books
        print books[0].title
        #print extra['search']
        #Book.objects.all().order_by('publication_date')[0:10]
        return render_to_response('booklist.tml',extra)
        #return HttpResponse(request.GET['search_text'])
    #books = None
    return render_to_response('booklist.tml',extra)
 

   

def new_comment(request,bookid):
    form = commentForm()
    extra = {}
    extra['form'] = form
    book = Book.objects.filter(id=bookid)
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1  
    if len(book) > 0:
        book = book[0]
    if 'userid' in request.session:
        user = User.objects.filter(id = request.session['userid'])[0]
        eval = evaluation.objects.filter(user=user, book=book)
        if len(eval) > 0:
            logger.info(EVA_CHOICE[eval[0].score/2 - 1][1])
            var = '%s' % eval[0].score
            form = commentForm(initial={'evaluate':EVA_CHOICE[eval[0].score/2 - 1][0]})
        if request.method == 'POST':
            form = commentForm(request.POST)
            if(form.is_valid()):
                cd = form.cleaned_data
                comment = Comment(title=cd['title'],date=datetime.datetime.now(),evaluateion=cd['evaluate'],user=user,contents=cd['contents'],book=book,rate=0,derate=0)
                comment.save()
                eval = evaluation.objects.filter(user = user,book = book)
                if len(eval) != 0:
                    eval[0].score = cd['evaluate']
                    eval[0].save()
                else:
                    eval= evaluation(score=cd['evaluate'],user = user,book = book)
                    eval.save()
                evals = evaluation.objects.filter(book = book)
                sum = 0
                for e in evals:
                    sum = sum + e.score
                eval = sum / len(evals)
                book.evaluation = eval
                book.save()
                list = List.objects.filter(user=user,book=book)
                if len(list) == 0:
                    list = List(user=user,book=book,status=u'已读',contents='',date=datetime.datetime.now())
                    list.save()
                else:
                    list = list[0]
                extra['form'] = form
                extra['user'] = user 
                extra['book'] = book
                extra['note'] = note
                extra['list'] = list
                return HttpResponseRedirect('%s%d' % ('/comment/',comment.id))
        extra['book'] = book
        extra['form'] = form
        return render_to_response('new_comment.tml',extra)
    else:
        #not login show error page
        extra['user'] = -1
        extra['form'] = form
        return render_to_response('error.tml',extra)
    return render_to_response('new_comment.tml',extra)

def new_note(request,bookid):
    form = noteForm()
    extra = {}
    extra['form'] = form
    book = Book.objects.filter(id=bookid)
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1  
    if len(book) > 0:
        book = book[0]
    if 'userid' in request.session:
        user = User.objects.filter(id = request.session['userid'])[0]
        eval = evaluation.objects.filter(user=user, book=book)
        if len(eval) > 0:
            form = commentForm(initial={'evaluate':EVA_CHOICE[eval[0].score/2 - 1][0]})
        if request.method == 'POST':
            form = noteForm(request.POST)
            if(form.is_valid()):
                cd = form.cleaned_data
                logger.info(cd['privilege'])
                note = Note(page = cd['page'],paragraph = cd['paragraph'],contents = cd['contents'],evaluateion = cd['evaluate'],user = user,book = book,privilege = cd['privilege'],date = datetime.datetime.now())
                note.save()
                eval = evaluation.objects.filter(user = user,book = book)
                if len(eval) != 0:
                    eval[0].score = cd['evaluate']
                    eval[0].save()
                else:
                    eval= evaluation(score=cd['evaluate'],user = user,book = book)
                    eval.save()
                evals = evaluation.objects.filter(book = book)
                sum = 0
                for e in evals:
                    sum = sum + e.score
                eval = sum / len(evals)
                book.evaluation = eval
                book.save()
                list = List.objects.filter(user = user,book = book)
                if len(list) == 0: 
                    list = List(user=user,book=book,status=u'读过',contents='',date = datetime.datetime.now())
                    list.save()
                extra['form'] = form
                extra['user'] = user 
                extra['book'] = book
                extra['note'] = note
                extra['list'] = list
                return HttpResponseRedirect('%s%d' % ('/note/' , note.id))
        extra['book'] = book
        return render_to_response('new_note.tml',extra)
    else:
        #not login show error page
        extra['user'] = -1
        return render_to_response('error.tml',extra)
    return render_to_response('new_note.tml',extra)



def book_notes(request,bookid):
    extra = {}
    book = Book.objects.filter(id = bookid)[0]
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
    else:
        extra['user'] = -1 
    notes = book.note_set.filter(privilege=1)
    extra['notes'] = notes
    extra['book'] = book
    return render_to_response('book_notes.tml',extra)

def latests(request):
    extra = {}
    if 'userid' in request.session:
        extra['user'] = User.objects.filter(id=request.session['userid'])[0]
    else:
        extra['user'] = -1  
    latest_books = Book.objects.all().order_by('publication_date')
    extra['latests'] = latest_books
    types = Type.objects.all()
    tagclasses = [[]]
    for type in types:
        tagclasses.append(popularTag(type))
    extra['tagclasses'] = tagclasses
    return render_to_response('latestbook.tml',extra)

def rate(request,commentid):
    extra = {}
    comment = Comment.objects.filter(id = commentid)[0]
    
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if comment.user.id != user.id:
            comment.rate = comment.rate +1
            comment.save()
            
    else:
        extra['user'] = -1  
       
    return HttpResponseRedirect('%s%d' % ('/comment/',comment.id))
    
    
def derate(request,commentid):
    extra = {}
    comment = Comment.objects.filter(id = commentid)[0]
    
    if 'userid' in request.session:
        user = User.objects.filter(id=request.session['userid'])[0]
        extra['user'] = user
        if comment.user.id != user.id:
            comment.derate = comment.derate +1
            comment.save()
           
    else:
        extra['user'] = -1 
       
    return HttpResponseRedirect('%s%d' % ('/comment/',comment.id))

def guess(request):
    extra = {}    
    if 'userid' in request.session:        
        userid = request.session['userid']
        user = User.objects.filter(id=userid)[0]  
        extra['user'] = user         
        rec = Recommendation('localhost', 'root', 'hehe', 'douban')
        recommand = rec.RecommendThroughTags(user.id)
        recommendations = []
        logger.info(recommand)
        for key in recommand.keys():
            logger.info(key)   
            recommendations.append(Book.objects.filter(id=key)[0])
        extra['recommendations'] = recommendations       
        return render_to_response('guess.tml',extra)    
    else:  
        extra['user'] = -1      
        return render_to_response('error.tml',extra)
