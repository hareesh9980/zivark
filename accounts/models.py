from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin',    'Admin'),
        ('engineer', 'Engineer'),
        ('sales',    'Sales'),
        ('manager',  'Manager'),
    ]

    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    full_name  = models.CharField(max_length=150, blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_engineer(self):
        return self.role == 'engineer'

    @property
    def is_sales(self):
        return self.role == 'sales'

    @property
    def is_manager(self):
        return self.role == 'manager'