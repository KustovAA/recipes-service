from django.contrib import admin

from .models import Unit, Ingredient, IngredientAndRecipe, Cuisine, Recipe, Category, User

admin.site.register(Unit)
admin.site.register(Ingredient)
admin.site.register(IngredientAndRecipe)
admin.site.register(Cuisine)
admin.site.register(Recipe)
admin.site.register(Category)
admin.site.register(User)
