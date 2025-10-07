from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import JobPosting, JobSeekerProfile, EmployerProfile, Application, Interview
from django import forms
from datetime import datetime
from django.db.models import Prefetch
from .forms import LoginForm  
from .utils import is_employer, is_employee 
# --- FORMS (Simple, non-ModelForms for direct user input) ---

# Simple Login Form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# Simple Job Posting Form
class JobPostingForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 5}))
    location = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}))

# Resume Upload Form
class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'resume']
        widgets = {
            'skills': forms.TextInput(attrs={'placeholder': 'e.g., Python, SQL, AWS', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'resume': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'})
        }

# Interview Scheduling Form
class InterviewForm(forms.ModelForm):
    # Use DateTimeInput for easier data input (though it requires browser support)
    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        initial=datetime.now()
    )
    class Meta:
        model = Interview
        fields = ['scheduled_time', 'location_link', 'notes']
        widgets = {
            'location_link': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3})
        }


# --- ROLE CHECKERS ---

def is_employee(user):
    """Checks if the user has a JobSeekerProfile."""
    return user.is_authenticated and hasattr(user, 'seeker_profile')

def is_employer(user):
    """Checks if the user has an EmployerProfile."""
    return user.is_authenticated and hasattr(user, 'employer_profile')

# --- AUTHENTICATION VIEWS ---

def user_login(request):
    """Handles login and redirects based on user role."""
    if request.user.is_authenticated:
        if is_employer(request.user):
            return redirect('employer_dashboard')
        elif is_employee(request.user):
            return redirect('employee_dashboard')
        # Fallback for admin users without specific profiles
        return redirect('employee_dashboard') 

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if is_employer(user):
                    messages.success(request, f"Welcome back, {user.username} (Employer)!")
                    return redirect('employer_dashboard')
                elif is_employee(user):
                    messages.success(request, f"Welcome back, {user.username} (Employee)!")
                    return redirect('employee_dashboard')
                else:
                    messages.info(request, "Logged in, but no employee or employer profile found.")
                    return redirect('employee_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {
        'form': form,
        'title': "Simple Role-Based Login"
    }
    return render(request, 'jobs/login.html', context)

@login_required
def user_logout(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- EMPLOYER VIEWS ---

@user_passes_test(is_employer, login_url='/')
@login_required
def employer_dashboard(request):
    """Employer dashboard showing posted jobs and applications."""
    try:
        employer_profile = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, "Employer profile not configured for this user.")
        return redirect('login') # or redirect to an admin setup page

    # Fetch jobs posted by the current employer, prefetching applications
    jobs = JobPosting.objects.filter(employer=employer_profile).prefetch_related(
        Prefetch(
            'applications',
            queryset=Application.objects.order_by('-applied_on').select_related(
                'seeker__user'
            ).prefetch_related('interview')
        )
    )

    context = {
        'employer': employer_profile,
        'jobs': jobs,
    }
    return render(request, 'jobs/employer_dashboard.html', context)

@user_passes_test(is_employer, login_url='/')
@login_required
def job_create(request):
    """Handles creating a new job posting."""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            JobPosting.objects.create(
                employer=request.user.employer_profile,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                location=form.cleaned_data['location']
            )
            messages.success(request, "Job posted successfully!")
            return redirect('employer_dashboard')
    else:
        form = JobPostingForm()
        
    context = {
        'form': form, 
        'title': "Post a New Job"
    }
    return render(request, 'jobs/job_form.html', context)

@user_passes_test(is_employer, login_url='/')
@login_required
def job_update(request, job_id):
    """Handles updating an existing job posting."""
    job = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job.title = form.cleaned_data['title']
            job.description = form.cleaned_data['description']
            job.location = form.cleaned_data['location']
            job.save()
            messages.success(request, f"Job '{job.title}' updated successfully.")
            return redirect('employer_dashboard')
    else:
        # Initialize form with current data
        initial_data = {'title': job.title, 'description': job.description, 'location': job.location}
        form = JobPostingForm(initial=initial_data)

    context = {
        'form': form,
        'job': job,
        'title': f"Update Job: {job.title}"
    }
    return render(request, 'jobs/job_form.html', context)

@user_passes_test(is_employer, login_url='/')
@login_required
def job_delete(request, job_id):
    """Deletes a job posting."""
    job = get_object_or_404(JobPosting, id=job_id, employer=request.user.employer_profile)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, f"Job '{job.title}' deleted.")
    return redirect('employer_dashboard')

@user_passes_test(is_employer, login_url='/')
@login_required
def shortlist_application(request, app_id):
    """Shortlists an application."""
    application = get_object_or_404(Application, id=app_id)
    if application.job.employer != request.user.employer_profile:
        messages.error(request, "Permission denied.")
        return redirect('employer_dashboard')

    if request.method == 'POST':
        application.status = 'SHORTLISTED'
        application.save()
        messages.success(request, "Application has been Shortlisted.")
    return redirect('employer_dashboard')

@user_passes_test(is_employer, login_url='/')
@login_required
def schedule_interview(request, app_id):
    """Schedules an interview for a shortlisted application."""
    application = get_object_or_404(Application, id=app_id)
    if application.job.employer != request.user.employer_profile:
        messages.error(request, "Permission denied.")
        return redirect('employer_dashboard')
    
    if application.status != 'SHORTLISTED' and application.status != 'INTERVIEW':
        messages.warning(request, "Application must be Shortlisted before scheduling.")
        return redirect('employer_dashboard')

    try:
        instance = application.interview
    except Interview.DoesNotExist:
        instance = None

    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=instance)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            
            application.status = 'INTERVIEW'
            application.save()
            messages.success(request, f"Interview scheduled for {application.seeker.user.username}.")
            return redirect('employer_dashboard')
    else:
        form = InterviewForm(instance=instance)
        
    context = {
        'form': form,
        'application': application,
        'title': f"Schedule Interview for {application.seeker.user.username}"
    }
    return render(request, 'jobs/schedule_interview.html', context)


# --- EMPLOYEE VIEWS ---

@user_passes_test(is_employee, login_url='/')
@login_required
def employee_dashboard(request):
    """Employee dashboard showing all jobs, their applications, and profile status."""
    try:
        seeker_profile = request.user.seeker_profile
    except JobSeekerProfile.DoesNotExist:
        # This shouldn't happen if setup is run, but as a safeguard:
        messages.error(request, "Employee profile not found. Please contact admin.")
        return redirect('login') 

    # Get all active jobs
    jobs = JobPosting.objects.filter(is_active=True).select_related('employer__user')

    # Get applications by this user, prefetching interview data
    applications = Application.objects.filter(seeker=seeker_profile).select_related('job').prefetch_related('interview')
    applied_job_ids = [app.job.id for app in applications]
    
    context = {
        'seeker_profile': seeker_profile,
        'jobs': jobs,
        'applications': applications,
        'applied_job_ids': applied_job_ids,
    }
    return render(request, 'jobs/employee_dashboard.html', context)

@user_passes_test(is_employee, login_url='/')
@login_required
def upload_resume(request):
    """Allows a job seeker to upload or update their resume/profile."""
    seeker_profile = get_object_or_404(JobSeekerProfile, user=request.user)

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=seeker_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume and profile updated successfully!")
            return redirect('employee_dashboard')
    else:
        form = ResumeUploadForm(instance=seeker_profile)

    context = {
        'form': form,
        'title': "Update Resume & Profile"
    }
    return render(request, 'jobs/upload_resume.html', context)


@user_passes_test(is_employee, login_url='/')
@login_required
def apply_for_job(request, job_id):
    """Handles the job application process."""
    job = get_object_or_404(JobPosting, id=job_id)
    seeker_profile = request.user.seeker_profile
    
    if not seeker_profile.resume:
        messages.error(request, f"Please upload your resume first to apply for: {job.title}.")
        return redirect('upload_resume')

    if Application.objects.filter(job=job, seeker=seeker_profile).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('employee_dashboard')
    
    Application.objects.create(
        job=job,
        seeker=seeker_profile,
        status='APPLIED'
    )
    messages.success(request, f"Successfully applied for '{job.title}'.")
    return redirect('employee_dashboard')
