import base64
import json
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from constants import MAX_NAME_IMAGE, MAX_UUID_LENGTH
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


User = get_user_model()


class Command(BaseCommand):
    """Загрузка файлов из JSON файлов."""

    DATA_PATH = 'recipes/data/'
    CSV_ENCODING = 'utf-8'

    help = 'Load data from CSV files into database'

    def handle(self, *args, **options):
        """Основной метод обработки команды."""
        loaders = {
            'users.json': (User, self.load_users),
            'recipes.json': (Recipe, self.load_recipes),
        }

        for filename, (model, func) in loaders.items():
            if model:
                func(filename, model)
            else:
                func(filename)
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))

    def load_users(self, filename, model):
        """Загрузка модели пользователей."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as jsonfile:
            users = json.load(jsonfile)

        for user_data in users:
            user, created_flag = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created_flag:
                user.set_password(user_data['password'])
                user.save()

    def load_recipes(self, filename, model):
        """Загрузка модели рецептов."""
        with open(
            f'{self.DATA_PATH}{filename}', encoding=self.CSV_ENCODING
        ) as jsonfile:
            recipes = json.load(jsonfile)

        for recipe_data in recipes:
            image_data = recipe_data['image']
            clean_name = slugify(recipe_data['name'])[:MAX_NAME_IMAGE]
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            uuid_str = str(uuid.uuid4()).replace("-", "")
            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=(f'recipe_{clean_name}{uuid_str[:MAX_UUID_LENGTH]}'
                      f'.{ext}')
            )

            author = User.objects.get(id=recipe_data['author'])

            recipe = Recipe.objects.create(
                author=author,
                name=recipe_data['name'],
                image=image_file,
                text=recipe_data['text'],
                cooking_time=recipe_data['cooking_time']
            )

            tags = Tag.objects.filter(id__in=recipe_data['tags'])
            recipe.tags.set(tags)

            for ing in recipe_data['ingredients']:
                ingredient = Ingredient.objects.get(id=ing['id'])
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ing['amount']
                )
