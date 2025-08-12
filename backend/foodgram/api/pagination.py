from rest_framework.pagination import PageNumberPagination

from constants import MAX_NAME_LENGTH, PAGE_SIZE


class FoodgramPageNumberPagination(PageNumberPagination):
    """Кастомный пагинатор с настройками по умолчанию.

    Количество элементов на странице - 6.
    Параметр запроса для указания количества элементов на странице - limit.
    """

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = MAX_NAME_LENGTH
