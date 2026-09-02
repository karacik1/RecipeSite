from django.contrib import admin
from .models import Recipe, Category, ParseredSites, ingredients_set, ingredient_forms


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', "ingredients", "created_at", "category"]
    list_filter = ("title", "created_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ParseredSites)
class ParsedSiteAdmin(admin.ModelAdmin):
    list_display = ["url", "parser_name"]

@admin.register(ingredients_set)
class IngredientsSetAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(ingredient_forms)
class IngredientFormsAdmin(admin.ModelAdmin):
    list_display = ["ingredient_form", "ingredient_correct_form"]
