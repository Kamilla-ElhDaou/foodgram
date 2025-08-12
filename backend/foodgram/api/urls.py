from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'},),
        name='users_subscriptions'
    ),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'), name='auth_logout'),
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
