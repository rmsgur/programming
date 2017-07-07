from django import forms
from .models import Post, Reply, UserItem

class PostForm(forms.ModelForm):
    image=forms.FileField()
    class Meta:
        model = Post
        fields = ('title', 'content', 'price', 'quantity', 'image',)

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('content', )

class UserItemForm(forms.ModelForm):
    class Meta:
        model = UserItem
        fields = ('quantity', 'phonenumber', 'address',)
