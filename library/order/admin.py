from django.contrib import admin
from .models import Order
from django.utils import timezone
from django.utils.html import format_html

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_info', 'user_info', 'created_at', 'end_at', 'planned_end_at', 'is_overdue')
    list_filter = ('created_at', 'end_at', 'planned_end_at')
    search_fields = ('book__name', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'get_status')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('book', 'user', 'created_at')
        }),
        ('Return Information', {
            'fields': ('end_at', 'planned_end_at', 'get_status'),
            'classes': ('collapse',)
        }),
    )
    
    def book_info(self, obj):
        return f"{obj.book.name} (ID: {obj.book.id})"
    book_info.short_description = 'Book'
    
    def user_info(self, obj):
        return f"{obj.user.get_full_name() or obj.user.email}"
    user_info.short_description = 'User'
    
    def get_status(self, obj):
        if obj.end_at:
            return 'Returned'
        if obj.planned_end_at and obj.planned_end_at < timezone.now():
            return format_html('<span style="color: red;">Overdue</span>')
        return 'On time'
    get_status.short_description = 'Status'
    get_status.allow_tags = True
    
    def is_overdue(self, obj):
        return self.get_status(obj)
    is_overdue.short_description = 'Status'
    is_overdue.allow_tags = True

admin.site.register(Order, OrderAdmin)
