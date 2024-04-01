from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import string 
import random
from uuid import uuid4
from datetime import datetime
from django.utils.timezone import now
# Create your models here.
User = get_user_model()
class Book(models.Model):
    PUBLIC_OR_PRIVATE =[
        ("Public","Public"),
        ("Private","Private")
    ]
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    review = models.TextField()
    public_or_private = models.CharField(max_length=20,choices=PUBLIC_OR_PRIVATE,default="Public")
    pdf = models.FileField(upload_to='books/',blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True)
    slug = models.SlugField(max_length=250,unique=True,null=False,blank=True)
    update = models.DateTimeField(auto_now=True,blank=True)
    create = models.DateTimeField(auto_now_add=True,blank=True)

    class Meta:
        ordering = ["-update","-create"]

    def _get_random(self):
        choice = string.ascii_uppercase+string.digits
        return "".join(random.choice(choice) for _ in range(5))

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Book.objects.filter(slug=unique_slug).exists():
            random_choice =self._get_random()
            unique_slug = '{}-{}'.format(slug,random_choice)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("books:book_detail", kwargs={"slug": self.slug})
    
class Profile(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=False)
    avatar = models.ImageField(upload_to='profile_picture/',null=True,blank=True)
    username = models.CharField(max_length=200)
    user = models.OneToOneField(get_user_model(),on_delete=models.CASCADE,null=False,blank=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("books:other_profile", kwargs={"pk": self.pk})

class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,related_name="comments",blank=True)
    comment = models.TextField()
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,blank=True)
    comment_create = models.DateTimeField(auto_now=True,blank=True)

    def __str__(self):
        return self.comment