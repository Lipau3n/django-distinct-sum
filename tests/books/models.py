from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)


class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='authors')


class BookOrder(models.Model):
    ONLINE = 'online'
    OFFLINE = 'offline'
    TYPE_CHOICES = [
        (ONLINE, 'Online'),
        (OFFLINE, 'Offline'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='orders')
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
