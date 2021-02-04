from django import forms
from django.forms import ModelForm, Textarea
from .models import Post, Group, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст публикации",
            "group": "Группа",
            "image": "Изображение"
        }

        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Добавьте изображение к посту"
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {'text': Textarea(attrs={'cols': 82, 'rows': 7})}
        labels = {
            "text": ""}