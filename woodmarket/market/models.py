from django.db import models
from django.urls import reverse

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Product.Status.PUBLISHED)
class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})
    def __str__(self):
        return self.name
class Category(models.Model):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def get_absolute_url(self):
        return reverse('cat_slug', kwargs={'cat_slug': self.slug})
    def __str__(self):
        return self.name
class ProductDetails(models.Model):
    material = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    warranty_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.material} | {self.size} | {self.warranty_years} года"
class Product(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    objects = models.Manager()  # обычный менеджер
    published = PublishedManager()
    title = models.CharField(max_length=255, verbose_name="Название")
    tags = models.ManyToManyField('Tag', blank=True, related_name='products', verbose_name="Теги")
    cat = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)), default=Status.DRAFT, verbose_name="Статус")
    details = models.OneToOneField(ProductDetails, on_delete=models.PROTECT,  null=True, blank=True, verbose_name="Характеристики")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None, blank=True, null=True,verbose_name="Фото")
    class Meta:
        verbose_name = "Изделия"
        verbose_name_plural = "Изделия"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create']),
        ]
    def save(self, *args, **kwargs):
         if self.details is None:
             self.details = ProductDetails.objects.create(
                 material="Не указано",
                 size="Не указано",
                 warranty_years=2
             )
         super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    def __str__(self):
        return self.title
