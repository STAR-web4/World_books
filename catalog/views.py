from django.shortcuts import render, HttpResponseRedirect
from django.http.response import HttpResponseNotFound
from .models import Author, BookInstance, Book
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .forms import Form_add_author, Form_edit_author
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView


# Create your views here.

def index(request):
    text_head = 'На нашем сайте вы можете получить книги в электронном виде'
    books = Book.objects.all()
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact=2).count()
    authors = Author.objects.all()
    num_authors = Author.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {'text_head': text_head, 'books': books, 'num_books': num_books, 'num_instances': num_instances,
               'num_instance_available': num_instances_available, 'author': authors, 'num_authors': num_authors,
               'num_visits': num_visits}
    return render(request, 'catalog/index.html', context)


class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 3


class BookDetailView(DetailView):
    model = Book
    context_object_name = ('book')


class AuthorListView(ListView):
    model = Author
    paginate_by = 4


class AuthorDetailView(DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    # Универсальный класс представления списка книг
    # находящихся в заказе у текущего пользователя
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='2').order_by('due_back')


def about(request):
    text_head = 'Сведения о копмании'
    name = 'ООО "Интелектуальные информационные системы"'
    rab1 = 'Разработка приложений на основе' \
           'системного искуственного интелекта'
    rab2 = 'Распознавание обьектов дорожной инфраструктуры'
    rab3 = 'Создание графических АРТ-обьектов на основе' \
           ' систем искусственного интелекта'
    rab4 = 'Создание цифровых интерактивных книг, учебных пособий' \
           ' атвоматизированных обучающих систем'
    context = {'text_head': text_head, 'name': name,
               'rab1': rab1, 'rab2': rab2,
               'rab3': rab3, 'rab4': rab4}
    return render(request, 'catalog/about.html', context)


def contact(request):
    text_head = 'контакты'
    name = 'ООО "Интелектуальные информационные системы"'
    address = 'Москва, ул. Планетарная, д. 20, к. 1'
    tel = '495-345-45-45'
    email = 'iis_info@mail.ru'
    context = {'text_head': text_head, 'name': name,
               'address': address, 'tel': tel,
               'email': email}
    return render(request, 'catalog/contact.html', context)


def edit_authors(request):
    author = Author.objects.all()
    context = {'author': author}
    return render(request, 'catalog/edit_authors.html', context)


def add_author(request):
    if request.method == 'POST':
        form = Form_add_author(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            about = form.cleaned_data.get('about')
            photo = form.cleaned_data.get('photo')
            # создать отбект для записи а БД
            obj = Author.objects.create(first_name=first_name, last_name=last_name,
                                        date_of_birth=date_of_birth, about=about, photo=photo)
            obj.save()
            return HttpResponseRedirect(reverse('authors-list'))
    else:
        form = Form_add_author()
        context = {'form': form}
        return render(request, 'catalog/authors_add.html', context)


def delete(request, id):
    try:
        author = Author.objects.get(id=id)
        author.delete()
        return HttpResponseRedirect('/edit_authors/')
    except:
        return HttpResponseNotFound('<h2>Автор не найден</h2>')


def edit_author(request, pk):
    author = Author.objects.get(pk=pk)
    if request.method == 'POST':
        instance = Author.objects.get(pk=pk)
        form = Form_edit_author(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/edit_authors/')
    else:
        form = Form_edit_author(instance=author)
        content = {"form": form}
        return render(request, 'catalog/edit_author.html', content)


def edit_books(request):
    book = Book.objects.all()
    context = {'book': book}
    return render(request, 'catalog/edit_books.html', context)


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('edit_books')


class BookUpdate(UpdateView):  # template_name_suffix -> book_form.html
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('edit_books')


class BookDelete(DeleteView):  # model_name_confirm_delete.html -> book_confirm_delete.html
    model = Book
    success_url = reverse_lazy('edit_books')


def book_add(request, pk):
    book = BookInstance.objects.get(pk=pk)
