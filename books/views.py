from django.shortcuts import render
from django.views.generic import View,TemplateView,ListView,DeleteView,DetailView,CreateView,UpdateView
from books.models import Book,Profile,Comment
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404,redirect
import os
from django.urls import reverse
from books.forms import BookUpdateForm,BookCreateForm,CommentForm,ProfileCreateUpdateForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.db.models import Q
# Create your views here.

class HomeView(TemplateView):
    template_name = "books/home.html"
class BookList(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def get_queryset(self):
        object = Book.objects.filter(public_or_private="Public")
        return object

class BookDetail(View):
    def get(self,request,slug):
        book = Book.objects.get(slug=slug)
        if(self.request.user != book.user):
            book = Book.objects.get(slug=slug,public_or_private="Public")
        return render(request, "books/book_detail.html", {"book":book})

class Mixin1(UserPassesTestMixin):
    def test_func(self):
        return Profile.objects.filter(user=self.request.user).exists()
class BookCreate(Mixin1,LoginRequiredMixin, CreateView):
    model = Book
    template_name = "books/book_create.html"
    fields = ["title","type","public_or_private","review","pdf"]

    def form_valid(self, form):
        object = form.save(commit=False)
        object.user = self.request.user
        object.save()
        return super().form_valid(form)


class BookUpdate(LoginRequiredMixin,UpdateView):
    model = Book
    template_name = "books/book_update.html"
    fields = ["title","type","public_or_private","review"]
    
    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        if object.user != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.slug=""
        return super().form_valid(form)

class BookDelete(LoginRequiredMixin,View):
    def get(self,request,slug):
        obj = get_object_or_404(Book,slug=slug)
        return render(request,'books/book_delete.html',{'book':obj})
    def post(self,request,slug):
        obj = get_object_or_404(Book,slug=slug)
        if obj.user!=self.request.user:
            raise PermissionDenied
        url = "media/"+obj.pdf.name
        os.remove(url)
        obj.delete()
        return redirect(reverse("books:book_list"))

class DownloadBook(View):
    def post(self,request,pk):
        obj = Book.objects.get(pk=pk)
        folder = obj.pdf.name.split('/')[0] + "/"
        fs = FileSystemStorage('media/'+folder)
        filename =  obj.pdf.name.split('/')[-1]
        if fs.exists(filename):
            with fs.open(filename) as pdf:
                response = HttpResponse(pdf,content_type='application/pdf')
                response['Content-Disposition'] = 'attachement; filename=%s'%(filename)
                return response
        else:
            return HttpResponseNotFound('The request pdf was not found.')

#Profile
class ProfileView(LoginRequiredMixin,View):
    def get(self,request):
        try:
            obj = Profile.objects.get(user=self.request.user)
        except:
             return HttpResponseRedirect(reverse("books:create-profile"))
        context = {"profile":obj}
        return render(request,'profile/profile.html',context)

class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    fields = ["username","avatar"]
    template_name = "profile/create_profile.html"

    def form_valid(self, form):
        if Profile.objects.filter(user=self.request.user).exists():
            return HttpResponse("Already Create.")
        form.instance.user = self.request.user
        return super().form_valid(form)

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = Profile
    template_name = "profile/profile_update.html"
    fields = ["username","avatar"]

class ProfileDetailViewOld(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profile/other_user_profile.html"
    context_object_name = "profile"

class ProfileDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        object = get_object_or_404(Profile,pk=pk)
        books = Book.objects.filter(user=object.user,public_or_private="Public")
        if object.user == self.request.user:
            return redirect(reverse("books:profile"))
        return render(request, "profile/other_user_profile.html",{"profile": object,"books":books})

class SearchView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"

    def get_queryset(self):
        search = self.request.GET.get("q")
        print(self.request.user)
        userbook = set()
        try:
            user= self.request.user
            userbook = Book.objects.filter(Q(title__icontains=search) | Q(user__profile__username__iexact=search) | Q(type__icontains=search)).filter(user=user,public_or_private="Private")
            book = Book.objects.filter(Q(title__icontains=search) | Q(user__profile__username__iexact=search) | Q(type__icontains=search)).filter(public_or_private="Public")
            books = userbook.union(book)
            return books
        except:
            book = Book.objects.filter(Q(title__icontains=search) | Q(user__profile__username__iexact=search) | Q(type__icontains=search)).filter(public_or_private="Public")
            return book


#Comment
class CommentView(LoginRequiredMixin,View):
    def get(self, request):
        book = get_object_or_404(Book,slug=request.GET.get("slug"))
        form = CommentForm()
        return render(request, "comments/create_comment.html", {"form":form,"slug":request.GET.get("slug")})
    def post(self,request):
        book = get_object_or_404(Book,slug=request.POST.get("slug"))
        slug = request.POST.get("slug")
        postvalue = dict()
        postvalue['csrfmiddlewaretoken'] = request.POST.get("csrfmiddlewaretoken")
        postvalue["comment"] = request.POST.get("comment")
        form = CommentForm(postvalue)
        if not form.is_valid():
            return render(request, 'comments/comment_create.html',{"form":form})
        form.instance.user = self.request.user
        form.instance.book = Book.objects.get(slug=slug)
        form.save()
        return redirect("/comments/"+slug)

class ShowComment(View):
    def get(self, request, slug):
        comment = Comment.objects.filter(book__slug=slug)
        return render(request, "comments/comments.html",{"comments":comment})

class ProfileUpdateNew(LoginRequiredMixin,View):
    def get(self,request,pk):
        object = get_object_or_404(Profile, pk=pk)
        form = ProfileCreateUpdateForm(initial=object)
        return render(request,"profile/profile_update.html",{"form":form})

class CommentDeleteView(LoginRequiredMixin,View):
    def get(self,request,pk,slug):
        object = get_object_or_404(Comment,pk=pk)
        if request.user != object.user:
            raise PermissionDenied
        object.delete()
        return redirect("/comments/"+slug)