from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200)  # Changed from author to authors
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(max_length=200, blank=True)
    thumbnail_url = models.URLField(blank=True)
    language = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.title

class BorrowedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    borrowed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
class borrowRequests(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    ], default='pending')


    def __str__(self):
        return f"{self.user.username} - {self.book.title}"