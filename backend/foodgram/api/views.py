from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FoodgramPageNumberPagination
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserAvatarSerializer, UserSerializer)
from constants import (HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_FORBIDDEN,
                       HTTP_METHOD_NOT_ALLOWED, HTTP_NO_CONTENT, HTTP_OK)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = FoodgramPageNumberPagination

    @action(detail=False, methods=['get'])
    def test(self, request):
        return Response(status=HTTP_OK)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Метод для создания страницы подписок."""
        queryset = User.objects.filter(
            subscribers__subscriber=self.request.user
        )
        if queryset:
            page = self.paginate_queryset(queryset)
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        return Response(
            {'subscriptions': 'Вы ни на кого не подписаны.'},
            status=HTTP_OK,
        )

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=SubscribeSerializer,
    )
    def subscribe(self, request, pk=None):
        """Метод для создания подписки/отписки на пользователя."""
        subscribed = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(
            subscriber=request.user,
            subscribed=subscribed,
        )

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'subscribe': 'Вы уже подписаны на данного пользователя'},
                    status=HTTP_BAD_REQUEST,
                )

            if request.user == subscribed:
                return Response(
                    {'subscribe': 'Вы не можете подписаться на себя'},
                    status=HTTP_BAD_REQUEST,
                )

            subscription = Subscription.objects.create(
                subscriber=request.user,
                subscribed=subscribed,
            )
            serializer = self.get_serializer(
                subscribed,
                context={'request': request},
            )
            return Response(serializer.data, status=HTTP_CREATED)

        if not subscription.exists():
            return Response(
                {'subscribe': 'Вы не подписаны на этого пользователя'},
                status=HTTP_BAD_REQUEST,
            )

        subscription.delete()
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
            user.avatar = None
            user.save()
            return Response(status=HTTP_NO_CONTENT)

        serializer = UserAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_OK)


class TagIngredientPermissionViewSet(viewsets.ModelViewSet):
    """Вьюсет с разрешениями для работы с тегами и ингредиентами."""

    def get_permissions(self):
        """Определяет разрешения в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return (permissions.IsAuthenticated(),)
        return (permissions.AllowAny(),)

    def _check_admin_or_405(self):
        """Проверяет, что пользователь - админ, иначе возвращает 405."""
        if not self.request.user.is_staff:
            return Response(
                {"detail": "Метод запрещен для не-администраторов"},
                status=HTTP_METHOD_NOT_ALLOWED,
            )
        return None

    def create(self, request, *args, **kwargs):
        """Создание объекта с проверкой прав администратора."""
        if (response := self._check_admin_or_405()) is not None:
            return response
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Обновление объекта с проверкой прав администратора."""
        if (response := self._check_admin_or_405()) is not None:
            return response
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление объекта с проверкой прав администратора."""
        if (response := self._check_admin_or_405()) is not None:
            return response
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Удаление объекта с проверкой прав администратора."""
        if (response := self._check_admin_or_405()) is not None:
            return response
        return super().destroy(request, *args, **kwargs)


class TagViewSet(TagIngredientPermissionViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(TagIngredientPermissionViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags', 'recipe_ingredients__ingredient', 'recipe_ingredients',
    )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('author__username', 'tags__slug')
    pagination_class = FoodgramPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """Определяет разрешения в зависимости от действия."""
        if self.action in ['list', 'retrieve', 'get_link']:
            return (permissions.AllowAny(),)
        return (permissions.IsAuthenticated(),)

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def update(self, request, *args, **kwargs):
        """Обновление рецепта с проверкой авторства."""
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'recipe': 'Вы не автор этого рецепта'},
                status=HTTP_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Удаление рецепта с проверкой авторства."""
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'recipe': 'Вы не автор этого рецепта'},
                status=HTTP_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)

        if request.method == 'POST':
            if favorite.exists():
                return Response(
                    {'favorite': 'Рецепт уже в избранном'},
                    status=HTTP_BAD_REQUEST,
                )
            favorite = Favorite.objects.create(
                user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(
                favorite, context={'request': request})
            return Response(serializer.data, status=HTTP_CREATED)

        if not favorite.exists():
            return Response(
                {'favorite': 'Рецепт не находится в избранном.'},
                status=HTTP_BAD_REQUEST,
            )
        favorite = Favorite.objects.get(user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=HTTP_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в корзине покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe,
        )

        if request.method == 'POST':
            if cart_item.exists():
                return Response(
                    {'shopping_cart': 'Рецепт уже в корзине'},
                    status=HTTP_BAD_REQUEST,
                )
            cart_item = ShoppingCart.objects.create(
                user=request.user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                cart_item, context={'request': request})
            return Response(serializer.data, status=HTTP_CREATED)

        if not cart_item.exists():
            return Response(
                {'shopping_cart': 'Рецепт не находится в корзине.'},
                status=HTTP_BAD_REQUEST,
            )
        cart_item = ShoppingCart.objects.get(user=request.user, recipe=recipe)
        cart_item.delete()
        return Response(status=HTTP_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачивание списка ингредиентов из рецептов в корзине покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        if not ingredients:
            return Response(
                {"detail": "Корзина пуста"},
                status=HTTP_BAD_REQUEST,
            )

        shopping_list = [
            (f"{ing['ingredient__name']} - {ing['total_amount']} "
             f"{ing['ingredient__measurement_unit']}")
            for ing in ingredients
        ]

        response = HttpResponse('\n'.join(shopping_list),
                                content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=True,
        methods=('get',),
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = f'https://foodgram.example.org/s/{pk}'
        return Response({'short-link': short_link}, status=HTTP_OK)
