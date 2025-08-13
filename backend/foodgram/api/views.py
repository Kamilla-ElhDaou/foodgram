from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Count, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrStaff
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserAvatarSerializer, UserSerializer)
from constants import (DOMAIN_NAME, HTTP_BAD_REQUEST, HTTP_CREATED,
                       HTTP_NO_CONTENT, HTTP_NOT_FOUND, HTTP_OK)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = FoodgramPageNumberPagination

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Метод для создания страницы подписок."""
        queryset = User.objects.filter(
            subscribers__subscriber=self.request.user
        ).annotate(recipes_count=Count('recipes')).order_by('username')

        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=SubscribeSerializer,
    )
    def subscribe(self, request, pk=None):
        """Метод для создания подписки/отписки на пользователя."""
        subscribed = get_object_or_404(
            User.objects.annotate(recipes_count=Count('recipes')),
            pk=pk
        )
        if request.method == 'POST':
            serializer = self.get_serializer(
                data={'subscribed': subscribed.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(subscriber=request.user)

            user_serializer = SubscriptionSerializer(
                subscribed,
                context={'request': request}
            )
            return Response(user_serializer.data, status=HTTP_CREATED)

        deleted_count, _ = Subscription.objects.filter(
            subscriber=request.user,
            subscribed=subscribed
        ).delete()

        if not deleted_count:
            return Response(
                {'subscribe': 'Вы не подписаны на этого пользователя'},
                status=HTTP_BAD_REQUEST
            )
        return Response(status=HTTP_NO_CONTENT)

    @action(
        detail=False,
        methods=('put', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        """Метод для добавления/удаления фотографии профиля."""
        user = request.user
        if request.method == 'DELETE':
            user.avatar.delete(save=False)
            user.save()
            return Response(status=HTTP_NO_CONTENT)

        serializer = UserAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_OK)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('author__username', 'tags__slug')
    pagination_class = FoodgramPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Возвращает кастомный QuerySet с аннотацией."""
        request = self.request
        queryset = Recipe.objects.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )

        if request and request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=request.user,
                        recipe=OuterRef('pk'),
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=request.user,
                        recipe=OuterRef('pk'),
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
            )

        return queryset

    def get_permissions(self):
        """Определяет разрешения в зависимости от действия."""
        if self.action in ['list', 'retrieve', 'get_link']:
            return (permissions.AllowAny(),)
        return (IsAuthorOrStaff(),)

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def handle_recipe_action(self, request, pk, serializer_class):
        """Общий метод для действий с рецептами в корзине и избранном."""
        recipe = get_object_or_404(Recipe, pk=pk)
        model_name = serializer_class.Meta.model
        item = model_name.objects.filter(user=request.user, recipe=recipe)

        if request.method == 'POST':
            if item.exists():
                return Response(
                    {'detail': 'Рецепт уже добавлен'},
                    status=HTTP_BAD_REQUEST,
                )
            item = model_name.objects.create(
                user=request.user, recipe=recipe)
            serializer = serializer_class(
                item, context={'request': request})
            return Response(serializer.data, status=HTTP_CREATED)

        if not item.exists():
            return Response(
                {'detail': 'Рецепт не добавлен'},
                status=HTTP_BAD_REQUEST,
            )
        item = model_name.objects.get(user=request.user, recipe=recipe)
        item.delete()
        return Response(status=HTTP_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        return self.handle_recipe_action(request, pk, FavoriteSerializer)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзине покупок."""
        return self.handle_recipe_action(request, pk, ShoppingCartSerializer)

    def get_shopping_cart_ingredients(self, user):
        """Получение ингредиентов из корзины."""
        return RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )

    def generate_shopping_list_text(self, ingredients):
        """Генерация текста списка покупок."""
        if not ingredients:
            return None

        return "\n".join(
            f"{ingredient['ingredient__name']} - {ingredient['total_amount']} "
            f"{ingredient['ingredient__measurement_unit']}"
            for ingredient in ingredients
        )

    def create_shopping_list_response(self, text_content):
        """Создание HTTP-ответа с файлом."""
        response = HttpResponse(
            text_content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        ingredients = self.get_shopping_cart_ingredients(request.user)
        shopping_list_text = self.generate_shopping_list_text(ingredients)

        if shopping_list_text is None:
            return Response(
                {'detail': 'Ваша корзина покупок пуста'},
                status=HTTP_BAD_REQUEST,
            )

        return self.create_shopping_list_response(shopping_list_text)

    @action(
        detail=True,
        methods=('get',),
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        if not Recipe.objects.filter(pk=pk).exists():
            return Response(
                {'recipe': 'Рецепт не найден'},
                status=HTTP_NOT_FOUND,
            )
        short_link = f'https://{DOMAIN_NAME}/s/{pk}'
        return Response({'short-link': short_link}, status=HTTP_OK)
