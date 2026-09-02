from django.contrib import admin
from .models import Recipe, Category, ParseredSites


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', "ingredients", "created_at", "category"]

    list_filter = ("title", "created_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ParseredSites)
class ParseredSiteAdmin(admin.ModelAdmin):
    list_display = ["url", "parser_name"]