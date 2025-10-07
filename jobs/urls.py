from django.urls import path
from . import views

urlpatterns = [
    # Custom Login/Logout (Root is the login page)
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Employee (Job Seeker) Routes
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/resume/upload/', views.upload_resume, name='upload_resume'),
    path('employee/apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    
    # Employer Routes (Dashboard and CRUD)
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/jobs/create/', views.job_create, name='job_create'),
    path('employer/jobs/update/<int:job_id>/', views.job_update, name='job_update'),
    path('employer/jobs/delete/<int:job_id>/', views.job_delete, name='job_delete'),
    
    # Employer Action: Shortlisting and Scheduling
    path('employer/application/shortlist/<int:app_id>/', views.shortlist_application, name='shortlist_application'),
    path('employer/application/schedule/<int:app_id>/', views.schedule_interview, name='schedule_interview'),
]
