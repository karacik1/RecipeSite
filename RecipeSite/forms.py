import select

from . import models
from .models import Recipe, Category
from django.forms import ModelForm, TextInput, DateTimeInput, Textarea, Select
class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ["title",
                  "category",
                  "ingredients",
                  "cooking_time",
                  "description",
                  ]
        widgets={
            "title":TextInput(attrs={
                'placeholder': "Название рецепта",
            }),
            "category":Select(attrs={
                "placeholder": "Выберите категорию",
            }),
            "ingredients": Textarea(attrs={
                'label': "Список ингридиентов",
            }),
            "cooking_time": DateTimeInput(attrs={
                "placeholder": "Время прирготовления",
            }),
            "description": Textarea(attrs={
                'placeholder': "Инструкция",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'
        self.fields["category"].queryset = Category.objects.all().order_by('name')




