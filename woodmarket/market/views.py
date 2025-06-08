from django.http import  HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Tag, UploadFiles
from .forms import AddProductForm, UploadFileForm
import uuid
# Create your views here.
menu = [
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить изделие", 'url_name': 'add_product'},
    {'title': "Обратная связь", 'url_name': 'contact'},
    {'title': "Войти", 'url_name': 'login'},
]
Product.objects.filter(is_published=1)

Categories = Category.objects.all()

def index(request):
    products = Product.published.all()
    categories = Category.objects.all()

    context = {
        'title': 'Главная страница',
        'posts': products,
        'categories': categories,
        'menu': menu,
        'cat_selected': 0,
    }
    return render(request, 'woodmarket/index.html', context)
def show_product(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    return render(request, 'woodmarket/product.html', {
        'title': product.title,
        'menu': menu,
        'product': product,
    })
# def handle_uploaded_file(f):
#     name = f.name
#     ext = ''
#
#     if '.' in name:
#         ext = name[name.rindex('.'):]
#         name = name[:name.rindex('.')]
#
#     suffix = str(uuid.uuid4())
#     with open(f"uploads/{name}_{suffix}{ext}", "wb+") as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)
def about(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fp = UploadFiles(file=form.cleaned_data['file'])
            fp.save()
    else:
        form = UploadFileForm()
    return render(request, 'woodmarket/about.html',{'title': 'О сайте', 'menu': menu, 'form': form})


def add_product(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                return redirect('home')  # или любой другой маршрут
            except Exception:
                form.add_error(None, 'Ошибка добавления изделия')
    else:
        form = AddProductForm()

    return render(request, 'woodmarket/add_product.html', {
        'title': 'Добавление изделия',
        'menu': menu,
        'form': form
    })
def contact(request):
    return HttpResponse("Обратная связь")

def login(request):
    return HttpResponse("Войти")

def show_category(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    posts = Product.objects.filter(cat_id=category.pk, is_published=True)

    context = {
        'menu': menu,
        'title': f'Рубрика: {category.name}',
        'posts': posts,
        'cat_selected': category.id,
    }

    return render(request, 'woodmarket/index.html', context)
def show_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = tag.products.filter(is_published=True)
    categories = Category.objects.all()

    context = {
        'title': f'Тег: {tag.name}',
        'posts': posts,
        'categories': categories,
        'menu': menu,
        'cat_selected': 0,
    }
    return render(request, 'woodmarket/index.html', context)
def categories_by_slug(request, cat_slug):
    if request.GET:
        print(request.GET)
        return HttpResponse("<h1>Статьи по категориям</h1>")

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

def archive(request, year):
    if year > 2025:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")
