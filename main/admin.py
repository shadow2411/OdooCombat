from django.contrib import admin
from .models import Book, BorrowedBook, borrowRequests

admin.site.register(Book)
admin.site.register(BorrowedBook)
admin.site.register(borrowRequests)
