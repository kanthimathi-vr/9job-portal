from django.contrib import admin
from .models import EmployerProfile, JobSeekerProfile, JobPosting, Application, Interview

# Define how models should appear in the admin
@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
    search_fields = ('company_name', 'user__username')

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'resume')
    search_fields = ('user__username', 'skills')

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'posted_on', 'is_active')
    list_filter = ('is_active', 'location')
    search_fields = ('title', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'seeker', 'status', 'applied_on')
    list_filter = ('status', 'job__title')
    search_fields = ('seeker__user__username', 'job__title')
    # Use fieldsets to make it easy to see which fields are required
    fieldsets = (
        (None, {
            'fields': ('job', 'seeker', 'status'),
        }),
    )

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_time', 'location_link')
    list_filter = ('scheduled_time',)
