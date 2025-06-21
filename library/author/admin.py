from django.contrib import admin
from .models import Author

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'patronymic', 'book_list')
    list_filter = ('surname', 'name')
    search_fields = ('surname', 'name', 'patronymic')
    filter_horizontal = ('books',)
    
    def book_list(self, obj):
        return ", ".join([book.name for book in obj.books.all()])
    book_list.short_description = 'Books'

admin.site.register(Author, AuthorAdmin)
