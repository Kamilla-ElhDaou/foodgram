from django.contrib import admin
from django.utils.html import format_html

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
    list_filter = ('measurement_unit',)


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
    search_fields = ('name', 'author__username', 'tags__name',)
    list_filter = ('tags', 'pub_date', 'author',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('pub_date',)

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
    search_fields = ('recipe__name', 'ingredient__name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Административная панель для избранных рецептов."""

    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Административная панель для корзины покупок."""

    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Административная панель для подписок пользователей."""

    list_display = ('subscriber', 'subscribed',)
    search_fields = (
        'subscriber__username',
        'subscribed__username',
    )
