from django.core.exceptions import ObjectDoesNotExist

from userprofile.models import UserProfile


def is_user_profile_owner(request, pk):
    try:
        user_profile = UserProfile.objects.get(id=pk)
        if request.user.is_authenticated:
            if request.user.is_staff:
                return True
            else:
                return user_profile.user == request.user
        else:
            return False
    except ObjectDoesNotExist:
        return None
