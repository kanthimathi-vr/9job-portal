from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

# --- Profile Models ---

class EmployerProfile(models.Model):
    """Profile for users who post jobs."""
    # This profile marks a user as an employer
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=150)
    company_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class JobSeekerProfile(models.Model):
    """Profile for users who seek jobs and upload resumes."""
    # This profile marks a user as an employee/job seeker
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seeker_profile')
    skills = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Python, SQL, AWS. Required before applying.")
    
    # Allow null/blank resume until the user uploads one
    resume = models.FileField(
        upload_to='resumes/',
        null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )

    def __str__(self):
        return f"Profile for {self.user.username}"

# --- Job Posting and Application Models (No Major Change) ---

class JobPosting(models.Model):
    """A job advertisement posted by an employer."""
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    """A record of a job seeker applying for a job."""
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview Scheduled'),
        ('REJECTED', 'Rejected'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')

    class Meta:
        unique_together = ('job', 'seeker') # Prevent duplicate applications

    def __str__(self):
        return f"{self.seeker.user.username} applied for {self.job.title} ({self.status})"

class Interview(models.Model):
    """Scheduling details for an interview."""
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
    scheduled_time = models.DateTimeField()
    location_link = models.URLField(max_length=255, blank=True, null=True, help_text="e.g., Google Meet or Zoom link")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interview for {self.application.seeker.user.username} on {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"
