from django.urls import path, re_path, register_converter
from market import views, converters
from django.conf import settings
from django.conf.urls.static import static

register_converter(converters.FourDigitYearConverter,"year4")


urlpatterns = [
 # re_path(r'^archive/(?P<year>[0-9]{4})/', views.archive),
 # path('archive/<year4:year>/', views.archive, name = 'archive'),
 path('about/', views.About.as_view(), name='about'),
 path('add/', views.AddProduct.as_view(), name='add_product'),
 path('', views.ProductHome.as_view(), name='home'),
 path('contact/', views.Contact.as_view(), name='contact'),
 path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
 path('product/<int:pk>/vote/', views.toggle_vote, name='toggle_vote'),
 path('product/<slug:slug>/', views.ShowProduct.as_view(), name= 'product'),
 path('product/<slug:slug>/edit/', views.UpdateProduct.as_view(), name= 'update_product'),
 path('product/<slug:slug>/delete/', views.DeleteProduct.as_view(), name= 'delete_product'),
 path('tag/<slug:tag_slug>/', views.ShowTag.as_view(), name='tag_slug'),
 path('cats/<slug:cat_slug>/', views.ShowCategory.as_view(), name='cat_slug'),
]

