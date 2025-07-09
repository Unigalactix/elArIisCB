from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Info', {
            'fields': ('employee_id', 'department', 'position', 'phone', 'avatar')
        }),
        ('Permissions', {
            'fields': ('is_hr', 'is_it_support')
        }),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'employee_id', 'department', 'is_staff']
    list_filter = ['is_staff', 'is_hr', 'is_it_support', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']

admin.site.register(User, CustomUserAdmin)