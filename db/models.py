import sys
from static_files.lang import Language as lang

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class User(models.Model):
    fullname = models.CharField(max_length=50, default="Dan")
    chat_id = models.CharField(max_length=25, default="123456789")
    age = models.IntegerField(default=0)
    gender = models.CharField(default='male', max_length=10)
    language_code = models.CharField(max_length=10, default=lang.uz_latn)
    date_of_created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_of_created']
        db_table = 'sys_users'

    def __str__(self):
        return self.fullname

    def update_last_login(self):
        self.last_login = models.DateTimeField(auto_now=True)
        self.save()
        return self.last_login


class Admin(models.Model):
    fullname = models.CharField(max_length=50, default="Dan")
    chat_id = models.CharField(max_length=25, default="123456789")
    date_of_created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        ordering = ['-date_of_created']
        db_table = 'sys_admins'

    def __str__(self):
        return self.fullname

    def update_last_login(self):
        self.last_login = models.DateTimeField(auto_now=True)
        self.save()
        return self.last_login


class Category(models.Model):
    name = models.CharField(max_length=50)
    owner_id = models.ForeignKey(Admin, on_delete=models.CASCADE)
    date_of_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['-date_of_created']
        db_table = 'categories'

    def __str__(self):
        return self.name


class Question(models.Model):
    question = models.CharField(max_length=250)
    date_of_created = models.DateTimeField(auto_now_add=True)
    photo_url = models.URLField(max_length=200, blank=True)
    categories = models.ManyToManyField(Category, related_name='questions')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['-date_of_created']
        db_table = 'questions'

    def __str__(self):
        return self.question


class Answer(models.Model):
    answer = models.CharField(max_length=250)
    date_of_created = models.DateTimeField(auto_now_add=True)
    photo_url = models.URLField(max_length=200, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['-date_of_created']
        db_table = 'answers'

    def __str__(self):
        return self.answer


class Channel(models.Model):
    channel_id = models.CharField(max_length=25)
    name = models.CharField(max_length=50)
    date_of_created = models.DateTimeField(auto_now_add=True)
    owner_id = models.ForeignKey(Admin, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'
        ordering = ['-date_of_created']
        db_table = 'channels'
