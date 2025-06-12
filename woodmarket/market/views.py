from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse, \
    HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .utils import DataMixin
from .forms import ContactForm, CommentForm
from django.contrib.auth.decorators import permission_required, login_required
from .models import Product, Category, Tag, ProductDetails, Comment, ProductVote
from .forms import AddProductForm, UploadFileForm
from django.views.generic import View, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView, TemplateView
# Create your views here.
Product.objects.filter(is_published=1)

Categories = Category.objects.all()

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user == comment.user or request.user.has_perm('market.can_delete_comment'):
        comment.delete()
        return redirect(comment.product.get_absolute_url())
    else:
        raise PermissionDenied
@login_required
@login_required
def toggle_vote(request, pk):
    product = get_object_or_404(Product, pk=pk)
    vote_type = request.GET.get("type")

    if vote_type not in ("like", "dislike"):
        return JsonResponse({"error": "Неверный тип"}, status=400)

    is_like = vote_type == "like"
    existing_vote = ProductVote.objects.filter(product=product, user=request.user).first()

    if existing_vote:
        if existing_vote.is_like == is_like:
            # Повторное нажатие на ту же кнопку — удаляем голос
            existing_vote.delete()
        else:
            # Переключение с лайка на дизлайк или наоборот
            existing_vote.is_like = is_like
            existing_vote.save()
    else:
        # Новый голос
        ProductVote.objects.create(product=product, user=request.user, is_like=is_like)

    return JsonResponse({
        "likes": product.votes.filter(is_like=True).count(),
        "dislikes": product.votes.filter(is_like=False).count(),
        "user_vote": None if not ProductVote.objects.filter(product=product, user=request.user).exists()
        else ProductVote.objects.get(product=product, user=request.user).is_like
    })
class ProductHome(DataMixin, ListView):
    template_name = 'woodmarket/index.html'
    title_page = 'Главная страница'
    context_object_name = 'posts'

    def get_queryset(self):
        return Product.published.all().select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']  # твои товары

        # Лайки и дизлайки по каждому товару
        likes = {}
        dislikes = {}
        for p in posts:
            likes[p.pk] = p.votes.filter(is_like=True).count()
            dislikes[p.pk] = p.votes.filter(is_like=False).count()

        context['likes'] = likes
        context['dislikes'] = dislikes

        # Голоса текущего пользователя
        user_votes = {}
        if self.request.user.is_authenticated:
            votes = ProductVote.objects.filter(user=self.request.user, product__in=posts)
            for vote in votes:
                user_votes[vote.product_id] = vote.is_like

        context['user_votes'] = user_votes
        return context
class ShowProduct(DataMixin, DetailView):
    model = Product
    template_name = 'woodmarket/product.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user')
        context['comment_form'] = CommentForm()
        context['likes'] = self.object.votes.filter(is_like=True).count()
        context['dislikes'] = self.object.votes.filter(is_like=False).count()

        # Добавляем текущий голос
        if self.request.user.is_authenticated:
            vote = self.object.votes.filter(user=self.request.user).first()
            context['user_vote'] = vote.is_like if vote else None
        else:
            context['user_vote'] = None

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.product = self.object
            comment.user = request.user
            comment.save()
            return redirect(self.object.get_absolute_url())
        return self.render_to_response(self.get_context_data(comment_form=form))

class About(LoginRequiredMixin, TemplateView):
    template_name = 'woodmarket/about.html'
    title_page = 'О сайте'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О сайте'
        return context
class AddProduct(LoginRequiredMixin, DataMixin, CreateView):
    model = Product
    template_name = 'woodmarket/add_product.html'
    form_class = AddProductForm
    success_url = reverse_lazy('home')
    title_page = 'Добавление мебели'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        d = ProductDetails.objects.create(
            warranty_years=form.cleaned_data.get('warranty_years') or 0,
            material=form.cleaned_data.get('material') or "Не указано",
            size=form.cleaned_data.get('size') or "Не указано"
        )
        self.object.details = d
        self.object.save()
        return redirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # передаём пользователя в форму
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)


class UpdateProduct(LoginRequiredMixin, DataMixin, UpdateView):
    model = Product
    template_name = 'woodmarket/add_product.html'
    permission_required = 'market.change_product'
    form_class = AddProductForm
    success_url = reverse_lazy('home')
    title_page = 'Редактирование данных о мебели'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.has_perm('market.change_product'):
            return HttpResponseForbidden("Вы не можете редактировать этот товар.")
        return super().dispatch(request, *args, **kwargs)
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
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # передаём пользователя в форму
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)
class DeleteProduct(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'woodmarket/delete_product.html'
    permission_required = 'market.del       ete_product'
    success_url = reverse_lazy('home')
    title_page = 'Удаление изделия'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.has_perm(self.permission_required):
            return HttpResponseForbidden("Вы не можете удалить этот товар.")
        return super().dispatch(request, *args, **kwargs)

class Contact(FormView):
    template_name = 'woodmarket/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')  # или укажи правильное имя для главной

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['username'] = self.request.user.username
        else:
            initial['username'] = 'Гость'
        return initial

    def form_valid(self, form):
        # здесь можешь добавить сохранение сообщения
        return super().form_valid(form)

class ShowCategory(DataMixin, ListView):
    template_name = 'woodmarket/index.html'
    context_object_name = 'posts'
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        return Product.published.filter(cat_id=self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']

        # Подсчёт лайков и дизлайков
        likes = {}
        dislikes = {}
        for p in posts:
            likes[p.pk] = p.votes.filter(is_like=True).count()
            dislikes[p.pk] = p.votes.filter(is_like=False).count()

        context['likes'] = likes
        context['dislikes'] = dislikes

        # Голоса текущего пользователя
        user_votes = {}
        if self.request.user.is_authenticated:
            votes = ProductVote.objects.filter(user=self.request.user, product__in=posts)
            for vote in votes:
                user_votes[vote.product_id] = vote.is_like

        context['user_votes'] = user_votes
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
        posts = context['posts']

        # Подсчёт лайков и дизлайков
        likes = {}
        dislikes = {}
        for p in posts:
            likes[p.pk] = p.votes.filter(is_like=True).count()
            dislikes[p.pk] = p.votes.filter(is_like=False).count()

        context['likes'] = likes
        context['dislikes'] = dislikes

        # Голоса текущего пользователя
        user_votes = {}
        if self.request.user.is_authenticated:
            votes = ProductVote.objects.filter(user=self.request.user, product__in=posts)
            for vote in votes:
                user_votes[vote.product_id] = vote.is_like

        context['user_votes'] = user_votes
        return self.get_mixin_context(
            context,
            title=f'Тег: {self.tag.name}',
            cat_selected=0
        )


def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

