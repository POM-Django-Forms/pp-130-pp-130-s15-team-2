from django import forms
from .models import Book
from author.models import Author

class BookForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False
    )
    
    class Meta:
        model = Book
        fields = ['name', 'description', 'count', 'publication_year', 'date_of_issue', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'count': forms.NumberInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        book = super().save(commit=False)
        if commit:
            book.save()
            self.save_m2m()
        return book
