from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Book, BorrowedBook, borrowRequests
from django.contrib.auth.decorators import login_required
from .utils.book_utils import populate_books_from_api
from django.db.models import Q
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def login_req(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            role = request.POST.get("role")

            user = authenticate(username=username, password=password)
            if user is not None:
                if role == "admin" and user.is_superuser:
                    login(request, user)
                    return redirect("admin_dashboard")
                elif role == "librarian" and user.is_staff:
                    login(request, user)
                    return redirect("librarian_dashboard")
                elif role == "user" and not user.is_staff and not user.is_superuser:
                    login(request, user)
                    return redirect("user_home")
                else:
                    form.add_error(None, "Invalid role selected for this user.")
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, "main/login.html", {"form": form})


def signup_req(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = request.POST.get("role", "user")

            if role == "librarian":
                user.is_staff = True
            elif role == "admin":
                user.is_superuser = True
                user.is_staff = True

            user.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Account created for {username} as {role}. You can now log in.",
            )
            return redirect("login")
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, "main/signup.html", {"form": form})


# @login_required
def user_homepage(request):
    if not request.user.is_authenticated:
        return redirect("login")
    user = request.user
    borrowed_books = BorrowedBook.objects.filter(user=user).select_related("book")

    context = {
        "user": user,
        "borrowed_books": borrowed_books,
    }
    return render(request, "main/user_homepage.html", context)


# @login_required
def search_books(request):
    if not request.user.is_authenticated:
        return redirect("login")
    query = request.GET.get("query", "")
    books = (
        Book.objects.filter(title__icontains=query)
        | Book.objects.filter(authors__icontains=query)
        | Book.objects.filter(isbn__icontains=query)
    )

    # If no books found in the database, fetch from API
    if not books.exists():
        populate_books_from_api(query)
        books = Book.objects.filter(title__icontains=query) | Book.objects.filter(
            authors__icontains=query
        )

    context = {
        "query": query,
        "books": books,
    }
    return render(request, "main/search_results.html", context)


# @login_required
def admin_dashboard(request):
    if not request.user.is_authenticated and not request.user.is_superuser:
        return redirect("login")
    if request.method == "POST":
        query = request.POST.get("query", "")
        saved_books = populate_books_from_api(query)
        messages.success(
            request, f"Successfully added {len(saved_books)} books to the database."
        )
    return render(request, "main/admin_dashboard.html")


# @login_required
def librarian_dashboard(request):
    if not request.user.is_staff:
        return redirect("login")
    # Add librarian dashboard logic here
    book_requests = borrowRequests.objects.filter(status="pending")
    approved_requests = borrowRequests.objects.filter(status="approved")
    return render(
        request,
        "main/librarian_dashboard.html",
        {"book_requests": book_requests, "approved_requests": approved_requests},
    )


# @login_required
def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Add user dashboard logic here
    return render(request, "user_dashboard.html")


# @login_required
def library_page(request):
    if not request.user.is_authenticated:
        return redirect("login")
    query = request.GET.get("query", "")
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query)
            | Q(authors__icontains=query)
            | Q(isbn__icontains=query)
        )
    else:
        books = Book.objects.all()
    books = Book.objects.all()
    # Pagination
    paginator = Paginator(books, 8)  # Show 8 books per page
    page = request.GET.get("page")
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        books = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        books = paginator.page(paginator.num_pages)

    return render(request, "main/library.html", {"books": books, "query": query})


# @login_required
def approve_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST" and request.user.is_staff:
        book_request = borrowRequests.objects.get(id=request_id)
        book_request.status = "approved"
        book_request.save()
        book = Book.objects.get(id=book_request.book.id)  # type: ignore
        borrowed_book = BorrowedBook(user=book_request.user, book=book)
        borrowed_book.due_date = datetime.now() + timedelta(days=14)
        borrowed_book.borrowed = True
        borrowed_book.save()
    return redirect("librarian_dashboard")


# @login_required
def add_librarian(request):
    if not request.user.is_staff:
        return redirect("login")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            messages.success(request, f"Librarian account created for {user.username}.")
            return redirect("admin_dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "main/admin_dashboard.html", {"form": form})


# @login_required
def deny_request(request, request_id):
    if request.method == "POST" and request.user.is_staff:
        book_request = borrowRequests.objects.get(id=request_id)
        book_request.status = "denied"
        book_request.save()
    return redirect("book_requests")


def logout_req(request):
    logout(request)
    return redirect("login")


# @login_required
def make_request(request, book_title):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        book = Book.objects.get(title=book_title)
        my_req = borrowRequests.objects.filter(user=request.user, book=book)
        my_borr = BorrowedBook.objects.filter(user=request.user, book=book)
        if my_req.exists() and my_borr.exists():
            return redirect("library")

        book_request = borrowRequests(user=request.user, book=book)

        # if request.user == book_request.user:
        #     return redirect('library')
        book_request.save()
        return redirect("library")
    return redirect("library")


def return_book(request, book_title):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        borrowed_book = BorrowedBook.objects.get(
            user=request.user, book__title=book_title
        )
        borrowed_book.delete()
    return redirect("user_home")
