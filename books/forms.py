from django import forms
from books.models import Book,Comment,Profile
class BookUpdateForm(forms.ModelForm):
    class Meta:
        model=Book
        fields=["title","review","pdf"]

class BookCreateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title","review","pdf"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]

class ProfileCreateUpdateForm(forms.Form):
    username = forms.CharField(max_length=200)
    profile_picture = forms.ImageField()