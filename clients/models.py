from django.db import models


class Client(models.Model):
    company_name   = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150)
    email          = models.EmailField(blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    address        = models.TextField(blank=True)
    city           = models.CharField(max_length=100, blank=True)
    industry       = models.CharField(max_length=100, blank=True)
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ['-created_at']