from django.utils import timezone, dateformat
from datetime import timedelta

def created_at_string(create_at):
    time = timezone.now() - create_at

    if time < timedelta(minutes=1):
        return '방금 전'
    elif time < timedelta(hours=1):
        return str(int(time.seconds / 60)) + '분 전'
    elif time < timedelta(days=1):
        return str(int(time.seconds / 3600)) + '시간 전'
    elif time < timedelta(days=7):
        time = timezone.now().date() - create_at.date()
        return str(time.days) + '일 전'
    else:
        return dateformat.format(create_at, 'Y.m.d H:i')