from rest_framework.pagination import PageNumberPagination


class FoodgramPageNumberPagination(PageNumberPagination):
    """
    Кастомный пагинатор с настройками по умолчанию.
    Количество элементов на странице - 6.
    Параметр запроса для указания количества элементов на странице - limit.
    """

    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100
