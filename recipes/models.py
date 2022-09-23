from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')


class Cuisine(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, verbose_name='Кухня')
    vegetarian = models.BooleanField(default=False, verbose_name='Вегетарианское?')
    spicy = models.BooleanField(default=False, verbose_name='Острое?')
    description = models.TextField(verbose_name='Рецепт')
    img = models.CharField(max_length=500, verbose_name='Картинка')


class IngredientAndRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингридиент')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт блюда')
    amount = models.IntegerField(default=0, verbose_name='Количество')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, verbose_name='Единица измерения')


class User(models.Model):
    first_name = models.CharField(max_length=200, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=200, null=True, verbose_name='Фамилия')
    phone = models.CharField(max_length=200, null=True, verbose_name='Телефон')
    email = models.EmailField(null=True, verbose_name='Почта')
    telegram_id = models.CharField(max_length=200, verbose_name='телеграм id')
    password = models.CharField(max_length=200, null=True, verbose_name='Пароль')
    likes = models.ManyToManyField(Recipe, related_name='likes', verbose_name='Понравившиеся')
    dislikes = models.ManyToManyField(Recipe, related_name='dislikes', verbose_name='Не понравившиеся')

