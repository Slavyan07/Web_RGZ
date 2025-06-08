from django import forms
from .models import Category, ProductDetails
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
    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория"
    )

    details = forms.ModelChoiceField(
        queryset=ProductDetails.objects.all(),
        required=False,
        empty_label="Не выбрано",
        label="Характеристики"
    )
    class Meta:
        model = Product
        fields = ['title', 'slug', 'description', 'is_published', 'cat', 'details', 'photo']
        labels = {
            'slug': 'URL',
            'description': 'Описание'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введите название'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'только латиница'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'cols': 60, 'rows': 5}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        allowed_chars = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя0123456789- "

        if not set(title) <= set(allowed_chars):
            raise forms.ValidationError("Название должно содержать только русские буквы, цифры, дефис и пробел.")

        if len(title) > 50:
            raise forms.ValidationError("Длина заголовка не должна превышать 50 символов.")

        return title

    # title = forms.CharField(
    #     max_length=255,
    #     min_length=5,
    #     label="Название",
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-input',
    #         'placeholder': 'Введите название'
    #     }),
    # )
    # def clean_title(self):
    #     title = self.cleaned_data['title']
    #     allowed = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя0123456789- "
    #
    #     if not set(title) <= set(allowed):
    #         raise forms.ValidationError("Название должно содержать только русские буквы, цифры, дефис и пробел.")
    #
    #     return title
    #
    # slug = forms.SlugField(
    #     label="URL (слаг)",
    #     widget=forms.TextInput(attrs={
    #         'class': 'form-input',
    #         'placeholder': 'только латиница, дефис и цифры'
    #     }),
    #     validators=[
    #         MinLengthValidator(5),
    #         MaxLengthValidator(100)
    #     ]
    # )
    #
    # description = forms.CharField(
    #     required=False,
    #     label="Описание",
    #     widget=forms.Textarea(attrs={
    #         'class': 'form-textarea',
    #         'cols': 60,
    #         'rows': 5,
    #         'placeholder': 'Описание изделия (необязательно)'
    #     })
    # )
    #
    # is_published = forms.BooleanField(
    #     required=False,
    #     label="Опубликовать",
    #     initial=True,
    #     widget=forms.CheckboxInput(attrs={
    #         'class': 'form-checkbox'
    #     })
    # )
    #
    # cat = forms.ModelChoiceField(
    #     queryset=Category.objects.all(),
    #     label="Категория",
    #     empty_label="Выберите категорию",
    #     widget=forms.Select(attrs={
    #         'class': 'form-select'
    #     })
    # )
    #
    # details = forms.ModelChoiceField(
    #     queryset=ProductDetails.objects.all(),
    #     required=False,
    #     label="Характеристики",
    #     empty_label="Не выбрано",
    #     widget=forms.Select(attrs={
    #         'class': 'form-select'
    #     })
    # )
