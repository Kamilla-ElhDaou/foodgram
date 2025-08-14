from admin_auto_filters.filters import AutocompleteFilter


class TagFilter(AutocompleteFilter):
    """Фильтр с автодополнением для модели тегов."""

    title = 'Тег'
    field_name = 'tags'


class RecipeFilter(AutocompleteFilter):
    """Фильтр с автодополнением для модели рецептов."""

    title = 'Рецепт'
    field_name = 'recipe'


class UserFilter(AutocompleteFilter):
    """Фильтр с автодополнением для модели пользователя."""

    title = 'Пользователь'
    field_name = 'user'


class IngredientFilter(AutocompleteFilter):
    """Фильтр с автодополнением для модели ингредиентов."""

    title = 'Ингредиент'
    field_name = 'ingredient'


class SubscriberFilter(AutocompleteFilter):
    """Фильтр с автодополнением для подписчиков."""

    title = 'Подписчик'
    field_name = 'subscriber'


class SubscribedFilter(AutocompleteFilter):
    """Фильтр с автодополнением для авторов, на которых подписаны."""

    title = 'Автор'
    field_name = 'subscribed'
