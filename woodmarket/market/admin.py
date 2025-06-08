from django.contrib import admin, messages
from .models import Product, Category
from django.utils.safestring import mark_safe

def pluralize_years(years: int) -> str:
    if 11 <= years % 100 <= 14:
        return "лет"
    last_digit = years % 10
    if last_digit == 1:
        return "год"
    elif 2 <= last_digit <= 4:
        return "года"
    return "лет"
# Register your models here.
class WarrantyRangeFilter(admin.SimpleListFilter):
    title = 'Срок гарантии'
    parameter_name = 'warranty'

    def lookups(self, request, model_admin):
        return [
            ('short', 'Менее 3 лет'),
            ('medium', 'От 3 до 5 лет'),
            ('long', 'Более 5 лет'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'short':
            return queryset.filter(details__warranty_years__lt=3)
        elif self.value() == 'medium':
            return queryset.filter(details__warranty_years__gte=3, details__warranty_years__lte=5)
        elif self.value() == 'long':
            return queryset.filter(details__warranty_years__gt=5)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'description', 'post_photo', 'photo', 'cat', 'details', 'tags']
    readonly_fields = ['post_photo']
    list_display = ('title', 'time_create', 'is_published', 'photo', 'cat', 'warranty_info', 'post_photo')
    filter_horizontal = ['tags']
    prepopulated_fields = {"slug": ("title",)}
    list_display_links = ('title',)
    list_editable = ('is_published',)
    ordering = ['time_create', 'title']
    actions = ['set_published', 'set_draft', 'extend_warranty']
    search_fields = ['title__startswith', 'cat__name']
    list_filter = [WarrantyRangeFilter, 'cat__name', 'is_published']

    @admin.display(description="Изображение ")
    def post_photo(self, product: Product):
        if product.photo:
            return mark_safe(f"<img src='{product.photo.url}' width = 150 > ")
        return "Без фото"

    @admin.display(description="Срок гарантии")
    def warranty_info(self, product: Product):
        word = pluralize_years(product.details.warranty_years)
        return f"{product.details.warranty_years} {word}"

    @admin.action(description="Опубликовать выбранные записи")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Изменено {count} записи(ей).")

    @admin.action(description="Снять с публикации выбранные записи")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count} записи(ей) сняты с публикации!", messages.WARNING)

    @admin.action(description="Продлить гарантию на 1 год")
    def extend_warranty(self, request, queryset):
        count = 0
        for product in queryset:
            if product.details:
                product.details.warranty_years += 1
                product.details.save()
                count += 1
        self.message_user(
            request,
            f"Гарантия продлена на 1 год у {count} изделия(ий).", messages.SUCCESS
        )
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
