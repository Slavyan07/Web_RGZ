from django.urls import path, re_path, register_converter
from market import views, converters
from django.conf import settings
from django.conf.urls.static import static

register_converter(converters.FourDigitYearConverter,"year4")


urlpatterns = [
 path('', views.index, name = 'home'),
 path('cats/<slug:cat_slug>/', views.show_category, name='cat_slug'),
 # re_path(r'^archive/(?P<year>[0-9]{4})/', views.archive),
 path('archive/<year4:year>/', views.archive, name = 'archive'),
 path('', views.index, name='home'),
 path('about/', views.about, name='about'),
 path('add/', views.add_product, name='add_product'),
 path('contact/', views.contact, name='contact'),
 path('login/', views.login, name='login'),
 path('product/<slug:product_slug>/', views.show_product, name='product'),
 path('tag/<slug:tag_slug>/', views.show_tag, name='tag'),
]

