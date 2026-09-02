from tkinter.constants import CASCADE

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def get_absolute_url(self):
        return reverse("main:recipe_list_by_category", args=[self.slug])

    def __str__(self):
        return self.name

class ingredients_set(models.Model):
    """Хранит название ингридиентов в им.п"""
    name = models.TextField(unique=True)
    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name

class Recipe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="recipies", null=True)

    title = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        ingredients_set,
        through="RecipeIngredient",
        related_name="recipies"
    )
    cooking_time = models.TextField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    original_URL = models.TextField(unique=True, blank=True, null=True)
    likes = models.IntegerField(default=0)
    tag = models.TextField()

    class Meta:
        ordering = ("title", 'created_at',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def get_absolute_url(self):
        return reverse("main:recipe_detail", args=[self.id])

    def __str__(self):
        return self.title
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(ingredients_set, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=True, null=True)
    extra = models.TextField(blank=True, null=True)
    raw_text = models.TextField()
    position = models.IntegerField(default=0)
    class Meta:
        ordering = ("position", )
        verbose_name = "Связь рецепта и ингредиента"
        verbose_name_plural = "Связь рецептов и ингредиентов"
    def __str__(self):
        return f'{self.recipe}: {self.ingredient}'


class ParseredSites(models.Model):
    url = models.TextField(unique=True)
    parser_name = models.TextField(max_length=200, null=True)

    class Meta:
        ordering = ("url", )
        verbose_name = "Сайт"
        verbose_name_plural = "Сайты"

    def __str__(self):
        return self.url



class ingredient_forms(models.Model):
    """Хранит имя ингридиента в различных падежах,
    имеет связку с общим список ингридиентов"""
    ingredient_form =models.TextField(unique=True)
    ingredient_correct_form = models.ForeignKey(ingredients_set, on_delete=models.CASCADE)

    def __str__(self):
        return self.ingredient_form