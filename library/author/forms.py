# forms.py
from django import forms
from .models import Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'surname', 'patronymic']
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name.replace(' ', '').replace('-', '').isalpha():
            raise forms.ValidationError('Please enter a valid first name (letters, spaces, hyphens only).')
        return name.title()

    def clean_surname(self):
        surname = self.cleaned_data.get('surname', '').strip()
        if not surname.replace(' ', '').replace('-', '').isalpha():
            raise forms.ValidationError('Please enter a valid last name (letters, spaces, hyphens only).')
        return surname.title()

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic', '').strip()
        if patronymic and not patronymic.replace(' ', '').replace('-', '').isalpha():
            raise forms.ValidationError('Patronymic can only contain letters, spaces, and hyphens.')
        return patronymic.title() if patronymic else ''
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        patronymic = cleaned_data.get('patronymic', '')

        # Перевірка унікальності (врахуй, що для редагування треба буде виключити поточного автора, це робиться у view)
        if Author.objects.filter(name__iexact=name, surname__iexact=surname, patronymic__iexact=patronymic).exists():
            raise forms.ValidationError('An author with this full name already exists.')
