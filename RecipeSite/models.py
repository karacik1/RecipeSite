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

class Recipe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="recipies", null=True)

    title = models.CharField(max_length=200)
    ingredients = models.TextField()
    cooking_time = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    original_URL = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("title", 'created_at',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def get_absolute_url(self):
        return reverse("main:recipe_detail", args=[self.id])

    def __str__(self):
        return self.title

class ParseredSites(models.Model):
    url = models.URLField(unique=True)
    parser_name = models.TextField(max_length=200, null=True)

    class Meta:
        ordering = ("url", )
        verbose_name = "Сайт"
        verbose_name_plural = "Сайты"

    def __str__(self):
        return self.url
