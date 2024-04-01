from django.urls import path
from django.views.generic import TemplateView
from . import views
app_name = 'books'
urlpatterns = [

    path("",views.HomeView.as_view(),name="home"),

    path("books/",views.BookList.as_view(),name="book_list"),
    path("book/<slug:slug>/",views.BookDetail.as_view(),name="book_detail"),
    path("create/book/",views.BookCreate.as_view(),name="book_create"),
    path("update/book/<slug:slug>",views.BookUpdate.as_view(),name="book_update"),
    path("delete/book<slug:slug>",views.BookDelete.as_view(),name="book_delete"),
    path('download/<int:pk>/',views.DownloadBook.as_view(),name="download"),

    path('profile/',views.ProfileView.as_view(),name="profile"),
    path('create-profile/',views.ProfileCreateView.as_view(),name="create-profile"),
    path('profile/<uuid:pk>/',views.ProfileDetailView.as_view(),name="other_profile"),
    path('profile/edit/<uuid:pk>/',views.ProfileUpdateView.as_view(),name="profile_update"),

    path("search/",views.SearchView.as_view(),name="search_book"),

    path("comments/",views.CommentView.as_view(),name="comments"),
    path("comments/<slug:slug>/",views.ShowComment.as_view(),name="comment_s"),
    path("comments/delete/<int:pk>/<slug:slug>/",views.CommentDeleteView.as_view(),name="comment_delete"),

]