from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404
from decimal import *

class MyUserManager(BaseUserManager):
    def create_user(self, username, realname, email, phonenumber, address, password=None):
        if not email:
            raise ValueError('Users must have an E-mail')      
            messages.info(request, 'The Email is alreay Exist'.format(post.title))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            realname=realname,
            phonenumber=phonenumber,
            address=address,
        )
        user.total_score = 0.
        user.total_customer = 0
        user.avg_score = 0.
        user.total_price = 0
        user.money = 0
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_seller(self, username, email, phonenumber, address, introduce, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phonenumber=phonenumber,
            introduce=introduce,
            address=address,
        )
        user.total_score = 0.
        user.total_customer = 0
        user.avg_score = 0.
        user.is_seller = True
        user.total_price = 0
        user.money = 0
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, username, realname, email, phonenumber, address, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            password=password,
            email=self.normalize_email(email),
            realname=realname,
            phonenumber=phonenumber,
            address=address,
        )
        user.total_score = 0.
        user.total_customer = 0
        user.avg_score = 0.
        user.is_seller = True
        user.is_admin = True
        user.total_price = 0
        user.money = 0
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=12, unique=True)
    realname = models.CharField(max_length=12, default="")
    phonenumber = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    introduce = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    total_score = models.FloatField(default=0)
    total_customer = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0)
    image = models.FileField(upload_to='./images/', verbose_name="图片", default='./images/default_image.jpg')
    total_price = models.DecimalField(max_digits=25, decimal_places=2, default=0)
    money = models.DecimalField(max_digits=25, decimal_places=2, default=0)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['realname', 'email', 'phonenumber', 'address']

    def get_full_name(self):
        # The user is identified by their email address
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_image_url(self):
        return '%s%s' %(settings.MEDIA_URL, self.image)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def get_total_price(self):
        total_price = Decimal(0.0)
        useritems = UserItem.objects.filter(user_id=self)
        for useritem in useritems:
            if useritem.is_in_cart == True:
                total_price += useritem.quantity * get_object_or_404(Post, pk=useritem.item_id).price
        return total_price


class Post(models.Model):
    author = models.ForeignKey('MyUser')
    title = models.CharField(max_length=100, verbose_name="商品名")
    content = models.TextField(verbose_name="商品说明")
    created_at = models.DateTimeField(default=timezone.now)
    price = models.DecimalField(verbose_name="价格", max_digits=20, decimal_places=2)
    type = models.CharField(max_length=10, verbose_name="种类", default = "")
    image = models.FileField(upload_to='./images/', verbose_name="图片", default='./images/default_image.jpg')
    total_score = models.FloatField(default=0)
    total_customer = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0)
    quantity = models.IntegerField(verbose_name="商品数量")

    def get_image_url(self):
        return '%s%s' %(settings.MEDIA_URL, self.image)

class Reply(models.Model):
    post = models.ForeignKey('Post', related_name='replies', related_query_name='reply')
    author = models.ForeignKey('MyUser')
    content = models.TextField(verbose_name="内容", default = "")
    created_at = models.DateTimeField(default=timezone.now)
    score = models.FloatField(default=0)


class UserItem(models.Model):
    user_id = models.ForeignKey('MyUser')
    item_id = models.IntegerField()
    product_author = models.CharField(max_length=11)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(verbose_name="购买数量", default=1)
    phonenumber = models.CharField(verbose_name="手机号", max_length=11)
    address = models.CharField(verbose_name="地址", max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    item_title = models.CharField(max_length=100)

    is_purchased = models.BooleanField(default=False)
    is_in_cart = models.BooleanField(default=False)
    is_scored = models.BooleanField(default=False)
    is_sended = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)

    def get_image_url(self):
        return '%s%s' %(settings.MEDIA_URL, get_object_or_404(Post, pk=self.item_id).image)

    def get_price(self):
        return get_object_or_404(Post, pk=self.item_id).price

    def get_total_price(self):
        return get_object_or_404(Post, pk=self.item_id).price * self.quantity
