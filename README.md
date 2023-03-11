# Django distinct SUM

Solves the django distinct sum problem

## Problem

[Django combining multiple aggregations](https://docs.djangoproject.com/en/4.1/topics/db/aggregation/#combining-multiple-aggregations)

Combining multiple aggregations with annotate() will yield the wrong results because joins are used instead of 
subqueries. Why Sum(..., distinct=True) dont return a valid value? Because distinct applies to values inside aggregation
function instead of distinct rows.

```python
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


book = Book.objects.create(title="1984")
BookAuthor.objects.bulk_create(
    [
        BookAuthor(book=book),
        BookAuthor(book=book),
        BookAuthor(book=book),
        BookAuthor(book=book),
    ],
)
BookOrder.objects.bulk_create(
    [
        BookOrder(book=book, type=BookOrder.ONLINE, price=100),
        BookOrder(book=book, type=BookOrder.ONLINE, price=200),
        BookOrder(book=book, type=BookOrder.OFFLINE, price=100),
        BookOrder(book=book, type=BookOrder.OFFLINE, price=100),
    ],
)


qs = Book.objects.annotate(
    online_orders_sum=models.Sum('orders__price', filter=models.Q(orders__type=BookOrder.ONLINE)),
    total_orders_sum=models.Sum('orders__price'),
    authors_count=models.Count('authors'),
).filter(title="1984")
qs[0].online_orders_sum  # returns 1200 instead of 300
qs[0].total_orders_sum  # returns 2000 instead of 500
```

## Installation

```pip install django-distinct-sum```


## Usage

```python
from django_distinct_sum.aggregates import DistinctSum


qs = Book.objects.annotate(
    online_orders_sum=DistinctSum('orders__id', 'orders__price', filter=Q(orders__type=BookOrder.ONLINE)),
    total_orders_sum=DistinctSum('orders__id', 'orders__price'),
)
```