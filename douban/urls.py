# -*- coding: UTF-8 -*-
from django.conf.urls.defaults import patterns, include, url
from douban.books.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import a4dmin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'douban.views.home', name='home'),
    # url(r'^douban/', include('douban.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^account/?$','douban.books.views.account'),
    (r'^account/login/?$','douban.books.views.login'),
    (r'^account/register/?$','douban.books.views.register'),
    (r'^$','douban.books.views.splesh'),
    (r'^account/logout/?$','douban.books.views.logout'),
    (r'^book/(?P<bookid>\d+)/?$','douban.books.views.book'),
    (r'^user/(?P<userid>\d+)/?$','douban.books.views.user'),
    (r'^user/(?P<userid>\d+)/comments/?$','douban.books.views.user_comments'),
    (r'^user/(?P<userid>\d+)/notes/?$','douban.books.views.user_notes'),
    (r'^comment/(?P<commentid>\d+)/?$','douban.books.views.comment'),
    (r'^mine/?$','douban.books.views.mine'),
    (r'^note/(?P<noteid>\d+)/?$','douban.books.views.note'),
    (r'^latestbooks/?$','douban.books.views.latests'),
    (r'^tags/?$','douban.books.views.tags'),
    (r'^tag/(?P<tagid>\d+)/?$','douban.books.views.tag'),
    (r'^book/(?P<bookid>\d+)/rec/?$','douban.books.views.recommandations'),
    (r'^book/(?P<bookid>\d+)/comment/?$','douban.books.views.new_comment'),
    (r'^book/(?P<bookid>\d+)/note/?$','douban.books.views.new_note'),
    (r'^book/(?P<bookid>\d+)/notes/?$','douban.books.views.book_notes'),
    (r'^search/?$','douban.books.views.search'),
    (r'^book/(?P<bookid>\d+)/share/?$','douban.books.views.sharebook'),
    (r'^commnet/(?P<commentid>\d+)/rate/?$','douban.books.views.rate'),
    (r'^comment/(?P<commentid>\d+)/derate/?$','douban.books.views.derate'),
    (r'^movement/?$','douban.books.views.movement'),
    (r'^guess/?$','douban.books.views.guess'),
)
