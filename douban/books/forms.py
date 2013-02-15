# -*- coding: UTF-8 -*-
'''
Created on 2012-12-20

@author: edward
'''

from django import forms

class loginForm(forms.Form):
    email = forms.EmailField(label=u'邮箱'.encode('utf-8'))
    password = forms.CharField(widget=forms.PasswordInput,label=u'密码')
    
class registerForm(forms.Form):
    email = forms.EmailField(label=u'邮箱'.encode('utf-8'))
    username = forms.CharField(max_length=16,label=u'用户名')
    password = forms.CharField(widget=forms.PasswordInput,label=u'密码')
    
class replyForm(forms.Form):
    contents = forms.CharField(widget = forms.Textarea,label=u'')
    
EVA_CHOICE = (
('2',u'很差'),
('4',u'差'),
('6',u'一般'),
('8',u'好'),
('10',u'很好'),
)
    
class commentForm(forms.Form):
    title = forms.CharField(max_length=100,label=u'标题')
    evaluate = forms.ChoiceField(choices=EVA_CHOICE,label=u'评价')
    contents = forms.CharField(widget = forms.Textarea,label=u'内容')
    
PRI_CHOICE = (
('1',u'所有人可见'),
('0',u'仅自己可见'),
)


    
class noteForm(forms.Form):
    page = forms.IntegerField(label=u'页码')
    paragraph = forms.CharField(max_length=1024,label=u'段落')
    evaluate = forms.ChoiceField(choices=EVA_CHOICE,label=u'评价')
    contents = forms.CharField(widget = forms.Textarea,label=u'内容')
    privilege = forms.ChoiceField(choices=PRI_CHOICE,label=u'权限')
    
STATUS = (
(u'想读',u'想读'),
(u'在读',u'在读'),
(u'读过',u'读过'),
)

    
class accountForm(forms.Form):
    username = forms.CharField(max_length=16)
    
class sharebookForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS,label=u'状态')
    evaluate = forms.ChoiceField(choices=EVA_CHOICE,label=u'评价') 
    tags = forms.CharField(max_length=200,label=u'标签(多个标签用空格分隔,最多100个字)')
    contents = forms.CharField(widget = forms.Textarea,label=u'简短附注')

class tagForm(forms.Form):
    tagkey = forms.CharField(max_length=100,label=u'')
