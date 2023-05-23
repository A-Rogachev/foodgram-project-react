from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationWithLimit(PageNumberPagination):
    """
    Пагинатор с возможность изменения кол-ва выдаваемых на
    странице объектов
    """
    page_size_query_param = 'limit'
