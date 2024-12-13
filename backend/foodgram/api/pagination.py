from rest_framework.pagination import PageNumberPagination

from core.constants import PAGE_SIZE


class UserRecipePagination(PageNumberPagination):
    """Кастомный класс пагинации."""
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
