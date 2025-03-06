from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Book
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from .forms import LoanBookForm
import datetime
def index(request):
    """View function for the home page of the site."""

    # Count number of books
    num_books = Book.objects.count()

    # Count number of book instances
    num_instances = BookInstance.objects.count()

    # Count available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Count the number of authors
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Prepare context data
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalog/index.html', context)

from django.contrib.auth.mixins import LoginRequiredMixin

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book

class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/my_books.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter\
            (borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('author_list'))


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death', 'author_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        return HttpResponseRedirect(reverse('author_list'))


def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    try:
        author.delete()
        messages.success(request, (author.first_name + ' ' +author.last_name +" has been deleted"))
    except:
        messages.success(request, (author.first_name + ' ' +author.last_name + ' cannot be deleted. Books exist for this author'))
    return redirect('author_list')

class AvailBooksListView(generic.ListView):
    """Generic class-based view listing all books on loan. """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_available.html'
    paginate_by = 10
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').order_by('book__title')

def loan_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request, then process the form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = LoanBookForm(request.POST, instance=book_instance)

        # Check if the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required (set due date and update status of book)
            book_instance = form.save()
            book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=4)
            book_instance.status = 'o'
            book_instance.save()

            # Redirect to a new URL
            return HttpResponseRedirect(reverse('all_available'))
    else:
        # If this is a GET (or any other method), create the default form
        form = LoanBookForm(instance=book_instance, initial={'book_title': book_instance.book.title})

    return render(request, 'catalog/loan_book_librarian.html', {'form': form})


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'cover_image']

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()

        # Add selected genres (many-to-many relationship)
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return super().form_valid(form)


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'cover_image']

    def form_valid(self, form):
        post = form.save(commit=False)

        # Remove previously stored genres
        for genre in post.genre.all():
            post.genre.remove(genre)

        # Add selected genres from the form
        for genre in form.cleaned_data['genre']:
            theGenre = get_object_or_404(Genre, name=genre)
            post.genre.add(theGenre)

        post.save()
        return super().form_valid(form)

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    try:
        book.delete()
        messages.success(request, f'Book "{book.title}" has been deleted.')
    except:
        messages.error(request, f'Book "{book.title}" cannot be deleted.')

    return redirect('book_list')


