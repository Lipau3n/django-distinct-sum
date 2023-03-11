import os
import unittest
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.test import TestCase

from django_distinct_sum.aggregates import DistinctSum
from .books.models import Book, BookAuthor, BookOrder


def create_test_data() -> Book:
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
    return book


class DjangoSumProblemTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.book = create_test_data()

    def test(self):
        qs = Book.objects.annotate(
            online_orders_sum=Sum('orders__price', filter=Q(orders__type=BookOrder.ONLINE)),
            total_orders_sum=Sum('orders__price'),
            authors_count=Count('authors'),
        ).order_by('id')
        self.assertEqual(qs[0].online_orders_sum, Decimal(1200))  # instead of Decimal(300)
        self.assertEqual(qs[0].total_orders_sum, Decimal(2000))  # instead of Decimal(500)


class DistinctSumTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.book = create_test_data()

    def test(self):
        qs = Book.objects.annotate(
            online_orders_sum=DistinctSum('orders__id', 'orders__price', filter=Q(orders__type=BookOrder.ONLINE)),
            total_orders_sum=DistinctSum('orders__id', 'orders__price'),
        ).filter(id=self.book.id)
        self.assertEqual(qs[0].online_orders_sum, Decimal(300))
        self.assertEqual(qs[0].total_orders_sum, Decimal(500))


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    unittest.main()
