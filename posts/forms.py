from django.forms import ModelForm, TextInput

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': TextInput(attrs={'class': 'form-control',
                                     'placeholder': 'Введите текст'})}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
