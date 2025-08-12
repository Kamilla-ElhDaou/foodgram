import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Система фильтрации для модели рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        method='filter_tags_or'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags_or(self, queryset, name, value):
        """Фильтрация по ИЛИ (OR) - рецепт содержит хотя бы один тег."""
        if not value:
            return queryset

        q_objects = Q()
        for tag in value:
            q_objects |= Q(tags__slug=tag.slug)

        return queryset.filter(q_objects).distinct()

    def filter_is_favorited(self, queryset, name, value):
        """Показывает рецепты в избранном."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Показывает рецепты в корзине."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """Система фильтрации для модели ингредиентов."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
