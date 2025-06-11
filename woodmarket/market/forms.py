from django import forms
from .models import Category, ProductDetails, Comment
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from .models import Product, Category, ProductDetails

@deconstructible
class RussianValidator:
    ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя0123456789- "

    def __init__(self, message=None):
        self.message = message or "Разрешены только русские буквы, цифры, пробел и дефис."

    def __call__(self, value):
        if not set(value) <= set(self.ALLOWED_CHARS):
            raise ValidationError(self.message)

class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Изображение")
class AddProductForm(forms.ModelForm):
    warranty_years = forms.IntegerField(label='Срок гарантии', required=False,  min_value=0, max_value=50, error_messages={
            'invalid': 'Введите целое число.',
            'min_value': 'Значение не может быть отрицательным.'
        })
    material = forms.CharField(label='Материал', required=False)
    size = forms.CharField(label='Размер', required=False)

    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория"
    )

    class Meta:
        model = Product
        fields = ['title', 'slug', 'description', 'tags', 'is_published', 'cat', 'photo']
        labels = {
            'slug': 'URL',
            'description': 'Описание'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введите название'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'только латиница'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'cols': 60, 'rows': 5}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        allowed_chars = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя0123456789- "

        if not set(title) <= set(allowed_chars):
            raise forms.ValidationError("Название должно содержать только русские буквы, цифры, дефис и пробел.")

        if len(title) > 50:
            raise forms.ValidationError("Длина заголовка не должна превышать 50 символов.")

        return title

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # заберём пользователя из аргументов
        super().__init__(*args, **kwargs)

        if user and not user.is_staff:
            self.fields.pop('is_published')  # скрыть поле для обычных пользователей
class ContactForm(forms.Form):
    username = forms.CharField(label='Никнейм', disabled=True)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea,)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']