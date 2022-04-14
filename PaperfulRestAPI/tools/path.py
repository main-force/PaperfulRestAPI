def user_profile_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user/{0}/userprofile/{1}/image/{2}'.format(instance.user.id, instance.nickname, filename)