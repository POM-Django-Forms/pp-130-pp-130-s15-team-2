from django.contrib import admin
from .models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'count', 'publication_year', 'date_of_issue', 'authors_list')
    list_filter = ('publication_year',)
    search_fields = ('name', 'description')
    date_hierarchy = 'date_of_issue'
    readonly_fields = ('get_date_of_issue',)
    fieldsets = (
        ('Book Information', {
            'fields': ('name', 'description', 'count')
        }),
        ('Publication Details', {
            'fields': ('publication_year', 'date_of_issue'),
            'classes': ('collapse',)
        }),
    )
    
    def authors_list(self, obj):
        return ", ".join([f"{author.surname} {author.name[0]}." for author in obj.authors.all()])
    authors_list.short_description = 'Authors'
    
    def get_date_of_issue(self, obj):
        return obj.date_of_issue
    get_date_of_issue.short_description = 'Date of Issue (readonly)'

admin.site.register(Book, BookAdmin)
