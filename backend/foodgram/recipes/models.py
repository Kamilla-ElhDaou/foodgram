from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from constants import (MAX_MEASUREMENT_UNIT_LENGTH, MAX_NAME_LENGTH,
                       MIN_AMOUNT, MIN_COOKING_TIME)


User = get_user_model()


class Tag(models.Model):
    """
    Модель для тега.

    Атрибуты:
        name (CharField): Название тега.
        slug (SlugField): Уникальный идентификатор для URL.
    """

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_tag',
            )
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель для ингредиентов.

    Атрибуты:
        name (CharField): Название ингредиента.
        measurement_unit (CharField): Единица измерения.
    """

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """
    Модель для рецептов.

    Атрибуты:
        author (ForeignKey): Автора рецепта.
        name (CharField): Название рецепта.
        image (ImageField): Основное изображение рецепта.
        text (TextField): Подробное описание процесса приготовления.
        cooking_time (PositiveIntegerField): Время в минутах.
        tags (ManyToManyField): Теги категоризации рецепта.
        ingredients (ManyToManyField): Ингредиенты рецепта.
        pub_date (DateTimeField): Дата создания.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    text = models.TextField(verbose_name='Текстовое описание',)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)],
        verbose_name='Время приготовления в минутах',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиент',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов с количеством.

    Атрибуты:
        recipe (ForeignKey): Связанный рецепт.
        ingredient (ForeignKey): Используемый ингредиент.
        amount (PositiveIntegerField): Количество.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """
    Модель для избранных рецептов.

    Атрибуты:
        user (ForeignKey): Пользователь, добавивший в избранное.
        recipe (ForeignKey): Рецепт, добавленный в избранное.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """
    Модель корзины покупок для рецептов.

    Атрибуты:
        user (ForeignKey): Пользователь/владелец корзина.
        recipe (ForeignKey): Рецепт, добавленный в корзину.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт в корзине',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'


class Subscription(models.Model):
    """
    Модель подписок пользователей друг на друга.

    Атрибуты:
        subscriber (ForeignKey): Пользователь, который подписывается.
        subscribed (ForeignKey): Пользователь, на которого подписываются.
    """

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Кто подписан',
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='На кого подписан',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribed}'
