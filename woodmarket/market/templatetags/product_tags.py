from django import template
import market.views as views
from market.models import Category, Tag
from django.db.models import Count
from market.utils import menu

register = template.Library()

@register.simple_tag()
def get_categories():
 return views.Categories

@register.simple_tag()
def get_menu():
    return menu

@register.inclusion_tag('woodmarket/list_categories.html')
def show_product_categories(cat_selected=0):
    cats = Category.objects.annotate(total=Count("products")).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected}

@register.inclusion_tag('woodmarket/list_tags.html')
def show_all_tags():
    return {
        "tags": Tag.objects.annotate(total=Count("products")).filter(total__gt=0)
    }
