from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html

from recipes.admin_filters import (IngredientFilter, RecipeFilter,
                                   SubscribedFilter, SubscriberFilter,
                                   TagFilter, UserFilter)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административная панель для управления тегами."""

    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административная панель для управления ингредиентами."""

    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Встроенная форма для редактирования ингредиентов рецепта."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административная панель для управления рецептами."""

    list_display = ('name', 'author', 'cooking_time', 'display_tags',
                    'pub_date', 'display_image', 'favorites_count',)
    search_fields = ('name', 'author__username',)
    list_filter = (TagFilter,)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('pub_date',)

    def get_queryset(self, request):
        """Возвращает QuerySet с оптимизированными запросами к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            Prefetch('tags'),
            Prefetch('ingredients'),
        )

    def display_tags(self, obj):
        """Форматирует отображение тегов через запятую."""
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Теги'

    def display_image(self, obj):
        """Отображает миниатюру изображения в админке."""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.image.url
            )
        return "Нет изображения"
    display_image.short_description = 'Изображение'

    def favorites_count(self, obj):
        """Отображает общее число добавлений рецепта в избранное."""
        return obj.favorites.count()
    favorites_count.short_description = 'В избранном'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Административная панель для связи рецептов и ингредиентов."""

    list_display = ('recipe', 'ingredient', 'amount',)
    list_filter = (RecipeFilter, IngredientFilter)
    search_fields = ('recipe__name',)

    def get_queryset(self, request):
        """Возвращает QuerySet с оптимизированными запросами к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.select_related('recipe', 'ingredient')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Административная панель для избранных рецептов."""

    list_display = ('user', 'recipe',)
    list_filter = (UserFilter, RecipeFilter)
    search_fields = ('user__username',)

    def get_queryset(self, request):
        """Возвращает QuerySet с оптимизированными запросами к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Административная панель для корзины покупок."""

    list_display = ('user', 'recipe',)
    list_filter = (UserFilter, RecipeFilter)
    search_fields = ('user__username',)

    def get_queryset(self, request):
        """Возвращает QuerySet с оптимизированными запросами к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Административная панель для подписок пользователей."""

    list_display = ('subscriber', 'subscribed',)
    list_filter = (SubscriberFilter, SubscribedFilter)
    search_fields = ('subscriber__username',)

    def get_queryset(self, request):
        """Возвращает QuerySet с оптимизированными запросами к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.select_related('subscriber', 'subscribed')
