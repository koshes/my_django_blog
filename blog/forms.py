from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    # Форма для email рассылки
    name = forms.CharField(max_length=25, label='Имя пользователя')
    email = forms.EmailField(label='Email отправителя')
    to = forms.EmailField(label='Email получателя')
    comments = forms.CharField(required=False, label='Комментарий',
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField(label='Ваш запрос')
