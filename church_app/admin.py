from django.contrib import admin
from .models import Member, Attendance, Announcement


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'gender', 'department', 'date_joined']
    list_filter = ['gender', 'department', 'date_joined']
    search_fields = ['name', 'phone', 'email']
    date_hierarchy = 'date_joined'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'date', 'service_type', 'status', 'marked_by']
    list_filter = ['status', 'date', 'service_type']
    search_fields = ['member__name']
    date_hierarchy = 'date'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_posted', 'posted_by', 'is_active']
    list_filter = ['is_active', 'date_posted']
    search_fields = ['title', 'message']
    date_hierarchy = 'date_posted'
