from django.db import models
from django.utils import timezone
from datetime import timedelta

from phonenumber_field.modelfields import PhoneNumberField

from PaperfulRestAPI.tools.random_generator import get_sixteen_random_token


class CertificationNumber(models.Model):
    phone_number = PhoneNumberField()
    certification_number = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=3))
    num_failed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-create_at',)

    def __str__(self):
        return f'[{self.phone_number}]{self.certification_number}'


class PhoneNumberIdentifyToken(models.Model):
    phone_number = PhoneNumberField()
    token = models.CharField(max_length=32)
    create_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ('-create_at',)

    def save(self, *args, **kwargs):
        self.token = get_sixteen_random_token()
        super().save(*args, **kwargs)
