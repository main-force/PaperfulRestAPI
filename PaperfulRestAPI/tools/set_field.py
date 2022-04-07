def set_user_profile_to_request(request):
    request.data['writer'] = request.user.profile.all().first().id
