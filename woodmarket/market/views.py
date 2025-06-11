from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import  HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .utils import DataMixin
from django.core.paginator import Paginator

from .models import Product, Category, Tag, ProductDetails
from .forms import AddProductForm, UploadFileForm
from django.views.generic import View, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView, TemplateView
# Create your views here.
Product.objects.filter(is_published=1)

Categories = Category.objects.all()


class ProductHome(DataMixin, ListView):
    template_name = 'woodmarket/index.html'
    title_page = 'Главная страница'
    context_object_name = 'posts'

    def get_queryset(self):
        return Product.published.all().select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cat_selected'] = int(self.request.GET.get('cat_id', 0))
        return self.get_mixin_context(context)
class ShowProduct(DataMixin, DetailView):
    model = Product
    template_name = 'woodmarket/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context['product'].title)

class About(LoginRequiredMixin, TemplateView):
    template_name = 'woodmarket/about.html'
    title_page = 'О сайте'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О сайте'
        return context
class AddProduct(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'woodmarket/add_product.html'
    form_class = AddProductForm
    success_url = reverse_lazy('home')
    title_page = 'Добавление изделия'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        d = ProductDetails.objects.create(
            warranty_years=form.cleaned_data.get('warranty_years') or 0,
            material=form.cleaned_data.get('material') or "Не указано",
            size=form.cleaned_data.get('size') or "Не указано"
        )
        self.object.details = d
        self.object.save()
        return redirect(self.success_url)


class UpdateProduct(PermissionRequiredMixin, UpdateView):
    model = Product
    template_name = 'woodmarket/add_product.html'
    permission_required = 'market.add_product'
    form_class = AddProductForm
    success_url = reverse_lazy('home')
    title_page = 'Редактирование изделия'

    def get_initial(self):
        initial = super().get_initial()
        if self.object.details:
            initial.update({
                'warranty_years': self.object.details.warranty_years,
                'material': self.object.details.material,
                'size': self.object.details.size
            })
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        warranty_years = form.cleaned_data.get('warranty_years') or 0
        material = form.cleaned_data.get('material') or "Не указано"
        size = form.cleaned_data.get('size') or "Не указано"

        if self.object.details:
            self.object.details.warranty_years = warranty_years
            self.object.details.material = material
            self.object.details.size = size
            self.object.details.save()
        else:
            detail = ProductDetails.objects.create(
                warranty_years=warranty_years,
                material=material,
                size=size
            )
            self.object.details = detail
            self.object.save()

        return response
class DeleteProduct(PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'woodmarket/delete_product.html'
    permission_required = 'market.delete_product'
    success_url = reverse_lazy('home')
    title_page = 'Удаление изделия'

class Contact(DataMixin, TemplateView):
    template_name = 'woodmarket/contact.html'
    title_page = 'Обратная связь'

class ShowCategory(DataMixin, ListView):
    template_name = 'woodmarket/index.html'
    context_object_name = 'posts'
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        return Product.published.filter(cat_id=self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            title=f'Рубрика: {self.category.name}',
            cat_selected=self.category.id
        )
class ShowTag(DataMixin, ListView):
    template_name = 'woodmarket/index.html'
    context_object_name = 'posts'
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return self.tag.products.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return self.get_mixin_context(
            context,
            title=f'Тег: {self.tag.name}',
            cat_selected=0
        )

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

