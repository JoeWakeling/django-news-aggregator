from django.db import models


class Author(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name


class Story(models.Model):
    headline = models.CharField(max_length=64)
    category = models.CharField(max_length=6, choices=[
        ('pol', 'Politics'),
        ('art', 'Art'),
        ('tech', 'Technology'),
        ('trivia', 'Trivial'),
    ])
    region = models.CharField(max_length=2, choices=[
        ('uk', 'UK'),
        ('eu', 'Europe'),
        ('w', 'World')
    ])
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date = models.DateField()
    details = models.CharField(max_length=128)

    def __str__(self):
        return self.headline
