import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для работы с изображениями в формате base64."""

    def to_internal_value(self, data):
        """Преобразует строку base64 в файл изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'{uuid.uuid4()}.' + ext
            )

        return super().to_internal_value(data)


class UserCreateSerializer(BaseUserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password'
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователями."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def to_representation(self, instance):
        """Проверка аутентификации."""
        if not isinstance(instance, User):
            raise NotAuthenticated('Необходимо авторизоваться.')
        return super().to_representation(instance)

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на данного пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                subscriber=request.user,
                subscribed=obj
            ).exists()
        return False


class UserAvatarSerializer(serializers.Serializer):
    """Сериализатор для работы с аватаром пользователя."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ['avatar']

    def update(self, instance, validated_data):
        """Обновляет фото профиля."""
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепте."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def validate(self, data):
        """Проверка ингредиентов, тегов и времени приготовления."""
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Нужно добавить хотя бы один ингредиент'}
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться'}
            )

        existing_ids = set(Ingredient.objects.filter(
            id__in=ingredient_ids
        ).values_list('id', flat=True))

        if missing_ids := set(ingredient_ids) - existing_ids:
            raise serializers.ValidationError(
                {'ingredients': f'Ингредиенты не найдены: {missing_ids}'}
            )

        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Нужно выбрать хотя бы один тег'}
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'}
            )

        cooking_time = data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть более 1 мин'}
            )

        return data

    def create_ingredients(self, recipe, ingredients):
        """Запись ингредиентов в рецепт."""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    def update_recipe_relations(self, recipe, tags, ingredients):
        """Обновление связанных данных рецепта (теги и ингредиенты)."""
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        self.update_recipe_relations(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredient_ids
        )

        if len(existing_ingredients) != len(ingredient_ids):
            missing_ids = (set(ingredient_ids)
                           - {ing.id for ing in existing_ingredients})
            raise serializers.ValidationError(
                {'ingredients': ('Некоторые ингредиенты не найдены:'
                                 f' {missing_ids}')}
            )

        instance.ingredients.clear()
        self.update_recipe_relations(instance, tags, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Отображение рецепта в ответе."""
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого отображения рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Общий сериализатор для рецептов в избранном и корзине покупок."""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True,
    )

    class Meta:
        abstract = True
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        """Проверка корректности введеных данных."""
        request = self.context.get('request')
        recipe = self.context.get('recipe')
        model = self.Meta.model

        exists = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if exists:
                raise serializers.ValidationError(
                    {"detail": "Рецепт уже добавлен."}
                )

        elif request.method == 'DELETE' and not exists:
            raise serializers.ValidationError(
                {"detail": "Рецепт не добавлен."}
            )

        return data


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    """Сериализатор для рецептов в избранном."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в корзине покупок."""

    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображение списка подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(default=0, read_only=True,)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count', 'avatar',
        )

    def get_recipes(self, obj):
        """Получение рецептов пользователей."""
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        serializer = ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializer.data


class SubscribeSerializer(SubscriptionSerializer):
    """Сериализатор подписания на пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def validate(self, data):
        """Валидация данных подписки."""
        subscribed = data.get('subscribed')
        request = self.context.get('request')

        if request.user == subscribed:
            raise serializers.ValidationError(
                {'subscribe': 'Вы не можете подписаться на себя'}
            )

        if Subscription.objects.filter(
            subscriber=request.user,
            subscribed=subscribed
        ).exists():
            raise serializers.ValidationError(
                {'subscribe': 'Вы уже подписаны на данного пользователя'}
            )

        return data

    def get_is_subscribed(self, obj):
        """Отображение статуса подписки."""
        return True
