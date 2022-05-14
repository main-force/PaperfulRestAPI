from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from hitcount.models import HitCountMixin, HitCount
from django.urls import reverse


from account.models import User
from userprofile.models import UserProfile

POST_STATUS = (
    ('T', 'Temporary save'),
    ('O', 'Open'),
    ('P', 'Private'),
    ('B', 'Ban'),
)


class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


def _thumbnail_directory_path(instance, filename):
    return 'posts/{}/thumbnail/{}'.format(instance.id, filename)

# class Attention(models.Model):
#


class Post(models.Model, HitCountMixin):
    tags = models.ManyToManyField(Tag, through='PostTag', blank=True, related_name='posts')
    attention_user_profiles = models.ManyToManyField(UserProfile, through='Attention', blank=True, related_name='attention_posts')
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation'
    )

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    thumbnail = models.ImageField(blank=True, upload_to=_thumbnail_directory_path)
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    intro = models.TextField(blank=True)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    status = models.CharField(default='T', max_length=1, choices=POST_STATUS)

    def __str__(self):
        return self.title

    def current_hit_count(self):
        return self.hit_count.hits

    def get_absolute_url(self):
        return reverse('post:detail', args=(self.id,))


class Attention(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='post_attention_list_by_user_profile')
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='post_attention_list_by_post')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.user_profile.nickname}]{self.post.title}'


class PostTag(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.tag.name}]{self.post.title}'

