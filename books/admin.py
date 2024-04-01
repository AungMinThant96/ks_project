from django.contrib import admin

# Register your models here.
from books.models import Book,Comment,Profile

class CommentInline(admin.StackedInline):
    model = Comment

class BookAdmin(admin.ModelAdmin):
    inlines =[ CommentInline ]

admin.site.register(Book,BookAdmin)
admin.site.register(Comment)
admin.site.register(Profile)