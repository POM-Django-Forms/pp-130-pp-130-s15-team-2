from django import forms
from django.core.exceptions import ValidationError
from datetime import date
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
    
    def clean_publication_year(self):
        publication_year = self.cleaned_data.get('publication_year')
        if publication_year is None:
            raise ValidationError('Publication year is required.')
            
        current_year = date.today().year
        if publication_year > current_year:
            raise ValidationError('Publication year cannot be in the future.')
        if publication_year < 1000:
            raise ValidationError('Publication year must be a valid year (1000 or later).')
        return publication_year
        
    def clean_count(self):
        count = self.cleaned_data.get('count')
        if count < 0:
            raise ValidationError('Count cannot be negative.')
        return count
        
    def clean_cover_image(self):
        cover_image = self.cleaned_data.get('cover_image', False)
        if cover_image:
            if cover_image.size > 2 * 1024 * 1024:  # 2MB limit
                raise ValidationError('Image file too large ( > 2MB )')
            return cover_image
        return None
        
    def save(self, commit=True):
        # Save the book instance first
        book = super().save(commit=False)
        
        if commit:
            # Save the book to get an ID
            book.save()
            
            # Save many-to-many relationships
            self.save_m2m()
            
            # Explicitly save the authors if they exist in cleaned_data
            if 'authors' in self.cleaned_data:
                book.authors.set(self.cleaned_data['authors'])
        
        return book
