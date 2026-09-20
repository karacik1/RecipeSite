

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import choices


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



class Tag(models.Model):
    name = models.TextField(max_length=200)
    colour = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите HEX-код цвета (например, #FF0000 или #F00)'
            )
        ],
        default='#FFFFFF'
    )

class SubTag(models.Model):
    name = models.TextField(max_length=200)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    def __str__(self):
        return self.name

class ParseredSites(models.Model):
    """Хранит сайты, которые пользователи пытались спарсить, и метод-парсер"""
    url = models.TextField(unique= True)
    parser_name = models.TextField(max_length=200, blank=True)

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


class Recipe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="recipies", null=True)
    title = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(
        ingredients_set,
        through="RecipeIngredient",
        related_name="recipies"
    )
    recipe_img_url = models.URLField(blank=True)
    cooking_time = models.TextField(blank=True)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    original_URL = models.TextField(unique=True, blank=True)
    likes = models.PositiveSmallIntegerField(default=0)
    tags = models.ManyToManyField(SubTag, related_name='recipies')
    note = models.TextField(blank=True)
    class Meta:
        ordering = ("title", 'created_at',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def get_absolute_url(self):
        return reverse("main:recipe_detail", args=[self.id])

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    # сделан ноль. смотреть в тудус
    ingredient_id = models.ForeignKey(ingredients_set, on_delete=models.SET_NULL,blank=True, null=True)
    name = models.TextField(max_length=200)
    unit = models.TextField(max_length=100, blank=True, null=True)
    amount = models.CharField(null=True, blank=True)
    extra = models.TextField(blank=True, max_length=200)
    raw_text = models.TextField()

    # TODO: сделать что бы в бд можно было указывать число самому и бд сама заполняла посишн.
    #     хз но может не надо делать заполнение строк,
    #     если вручную заполняется в админке. а там я не собираюсь сама заниматься этим

    position = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ("position", )
        verbose_name = "Связь рецепта и ингредиента"
        verbose_name_plural = "Связь рецептов и ингредиентов"
    def __str__(self):
        return f'{self.recipe}: {self.name}'

class SuggestNewIngredientForms(models.Model):
    """Таблица для добавления новых форм значений к ингридиенту
    Например: """
    ingredient_form = models.CharField(max_length=200)
    class Meta:
        verbose_name = "Новая форма"
        verbose_name_plural = "Новые формы"

class IngredientSuggestion(models.Model):
    """Таблица для модерации новых ингридиентов"""
    STATUS_CHOICES = [
        ("pending", "На модерации"),
        ("rejected", "отклонено"),
        ("accepted", "разрешено"),
    ]

    ingredient_id = models.TextField(max_length=200)
    forms =  models.ForeignKey(SuggestNewIngredientForms, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default="pending", verbose_name="Статус")
    added_at = models.DateField(auto_now_add=True)
    moderated_at = models.DateField(auto_now=True, null=True)
    class Meta:
        ordering = ("-added_at", "moderated_at" )
        verbose_name = "Предложить ингридиент"
        verbose_name_plural = "Предложения ингридиентов"


