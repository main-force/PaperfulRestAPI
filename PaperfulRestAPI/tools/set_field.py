def set_user_profile_to_request(request):
    request.data['writer'] = request.user.profile.all().first().id


def set_post_to_request(request, post):
    request.data['post'] = post.id


def set_parent_comment_to_request(request, comment):
    request.data['parent_comment'] = comment.id
