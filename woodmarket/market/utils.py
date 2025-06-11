menu = [
    {'title': "Главная страница", 'url_name': 'home'},
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить изделие", 'url_name': 'add_product'},
    {'title': "Обратная связь", 'url_name': 'contact'},
]

class DataMixin:
    paginate_by = 5
    title_page = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page

    def get_mixin_context(self, context, **kwargs):
        if self.title_page:
            context['title'] = self.title_page
        context['cat_selected'] = None
        context.update(kwargs)
        return context
