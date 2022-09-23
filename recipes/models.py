from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=200)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)


class Cuisine(models.Model):
    name = models.CharField(max_length=200)


class Category(models.Model):
    name = models.CharField(max_length=200)


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True)
    vegetarian = models.BooleanField(default=False)
    spicy = models.BooleanField(default=False)
    description = models.TextField()
    img = models.CharField(max_length=500)


class IngredientAndRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)


class User(models.Model):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)
    telegram_id = models.CharField(max_length=200)
    password = models.CharField(max_length=200, null=True)
    likes = models.ManyToManyField(Recipe, related_name='likes')
    dislikes = models.ManyToManyField(Recipe, related_name='dislikes')

