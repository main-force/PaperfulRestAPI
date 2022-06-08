from django.core.exceptions import ObjectDoesNotExist

from post.models import Post
from comment.models import Comment
from report.models import ReportUserProfile, ReportPost, ReportComment
from userprofile.models import UserProfile

def get_post_object(pk):
    try:
        post = Post.objects.get(id=pk, status='O')
        return post
    except ObjectDoesNotExist:
        return None


def get_comment_object(pk):
    try:
        comment = Comment.objects.get(id=pk, status='O')
        return comment
    except ObjectDoesNotExist:
        return None


def get_parent_comment_object(pk):
    try:
        comment = Comment.objects.filter(parent_comment__isnull=True).get(id=pk)
        return comment
    except ObjectDoesNotExist:
        return None


def get_user_profile_object(pk):
    try:
        user_profile = UserProfile.objects.get(id=pk)
        return user_profile
    except ObjectDoesNotExist:
        return None


def get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
    try:
        comment = user_profile.attention_comments.get(pk=comment_pk, status='O')
        return comment
    except ObjectDoesNotExist:
        return None


def get_comment_in_user_profile_hide_comments(user_profile, comment_pk):
    try:
        comment = user_profile.hide_comments.get(pk=comment_pk, status='O')
        return comment
    except ObjectDoesNotExist:
        return None


def get_post_in_user_profile_attention_posts(user_profile, post_pk):
    try:
        post = user_profile.attention_posts.get(pk=post_pk, status='O')
        return post
    except ObjectDoesNotExist:
        return None


def get_post_in_user_profile_hide_posts(user_profile, post_pk):
    try:
        post = user_profile.hide_posts.get(pk=post_pk, status='O')
        return post
    except ObjectDoesNotExist:
        return None


def get_post_in_user_profile_bookmarks(user_profile, post_pk):
    try:
        post = user_profile.bookmarks.get(pk=post_pk, status='O')
        return post
    except ObjectDoesNotExist:
        return None


def get_user_profile_in_target_user_profile_subscribers(target_user_profile, user_profile_pk):
    try:
        user_profile = target_user_profile.subscribers.get(pk=user_profile_pk)
        return user_profile
    except ObjectDoesNotExist:
        return None


def get_user_profile_in_user_profile_subscriptions(user_profile, subscription_user_profile_pk):
    try:
        subscription_user_profile = user_profile.subscriptions.get(pk=subscription_user_profile_pk)
        return subscription_user_profile
    except ObjectDoesNotExist:
        return None


def get_user_profile_in_target_user_profile_hide_user_profiles(target_user_profile, user_profile_pk):
    try:
        user_profile = target_user_profile.hide_user_profiles.get(pk=user_profile_pk)
        return user_profile
    except ObjectDoesNotExist:
        return None


def get_report_user_profile_object(reporter_user_profile, reportee_user_profile):
    try:
        report = ReportUserProfile.objects.get(reporter=reporter_user_profile, reportee=reportee_user_profile)
        return report
    except ObjectDoesNotExist:
        return None


def get_report_post_object(reporter_user_profile, post):
    try:
        report = ReportPost.objects.get(reporter=reporter_user_profile, post=post)
        return report
    except ObjectDoesNotExist:
        return None


def get_report_comment_object(reporter_user_profile, comment):
    try:
        report = ReportComment.objects.get(reporter=reporter_user_profile, comment=comment)
        return report
    except ObjectDoesNotExist:
        return None
