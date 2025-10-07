from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

# --- Role Check Helper Functions (using Django Groups) ---

def is_employer(user: User) -> bool:
    """
    Checks if the given user belongs to the 'Employers' group.
    
    Args:
        user: A Django User object.
        
    Returns:
        True if the user is in the 'Employers' group, False otherwise.
    """
    # A standard and efficient way to check group membership
    return user.groups.filter(name='Employers').exists()

def is_employee(user: User) -> bool:
    """
    Checks if the given user belongs to the 'Employees' group.
    
    Args:
        user: A Django User object.
        
    Returns:
        True if the user is in the 'Employees' group, False otherwise.
    """
    # Note: If you have a separate profile model with a boolean field 
    # (e.g., user.profile.is_employee), you would use that instead.
    return user.groups.filter(name='Employees').exists()

# --- Alternative Implementation (If using a Custom User Model with a 'role' field) ---

# If you have defined a custom User model (e.g., in your app's models.py) like this:
# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('employer', 'Employer'),
#         ('employee', 'Employee'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

# ... then you would use this implementation instead:

# def is_employer_by_field(user):
#     return user.role == 'employer'

# def is_employee_by_field(user):
#     return user.role == 'employee'