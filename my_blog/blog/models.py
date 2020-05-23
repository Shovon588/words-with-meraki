from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.


class Story(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    story_name = models.CharField(max_length=256)
    story_trailer = models.TextField(blank=True)
    create_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.story_name


class Post(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(null=True, blank=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approve_comments(self):
        return self.comments.filter(approved_comment=True)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=150)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text


class About(models.Model):
    about = models.TextField()

    def __str__(self):
        return self.about


class ReaderInfo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='readerinfos')
    user_ip = models.CharField(max_length=100, unique=False)
    read_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s at %s" %(self.user_ip, self.read_time)