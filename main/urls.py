from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_page, name='index'),
    path('login/', views.login_req, name='login'),
    path('signup/', views.signup_req, name='signup'),
    path('user/home/', views.user_homepage, name='user_home'),
    path('user/search/', views.search_books, name='search_books'),
    path('admin-dash/', views.admin_dashboard, name='admin_dashboard'),
    path('library/', views.library_page, name='library'),
    path('logout/', views.logout_req, name='logout'),
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('request-book/<str:book_title>/', views.make_request, name='make_request'),
    path('return-book/<str:book_title>/', views.return_book, name='return_book'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('deny-request/<int:request_id>/', views.deny_request, name='deny_request'),
    path('add_librarian/', views.add_librarian, name='add_librarian'),
]