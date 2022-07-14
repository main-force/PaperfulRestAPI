from django.db import models
from django.utils import timezone
from datetime import timedelta

from phonenumber_field.modelfields import PhoneNumberField
from PaperfulRestAPI.tools.random_generator import get_sixteen_random_token
from django.utils.translation import gettext_lazy as _


def after_3minutes():
    return timezone.now() + timedelta(minutes=3)

class CertificationNumber(models.Model):
    phone_number = PhoneNumberField(help_text=_('+82010xxxxxxxx 형태로 입력해주십시오.'))
    certification_number = models.PositiveIntegerField(help_text=_('휴대폰번호 인증을 위한 인증번호. String이 아닌, Integer 타입입니다.'))
    create_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(default=after_3minutes)
    num_failed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-create_at',)

    def __str__(self):
        return f'[{self.phone_number}]{self.certification_number}'


class PhoneNumberIdentifyToken(models.Model):
    phone_number = PhoneNumberField(help_text=_('+82010xxxxxxxx 형태로 입력해주십시오.'))
    token = models.CharField(max_length=64, help_text=_('휴대폰 번호 획득을 위한 token값 입니다.'))
    create_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ('-create_at',)

    def save(self, *args, **kwargs):
        self.token = get_sixteen_random_token()
        super().save(*args, **kwargs)
