from _pyrepl import console

from urllib import request
from django.shortcuts import get_object_or_404
from unicodedata import category
from RecipeSite.models import Category, Recipe, ParseredSites
from RecipeSite.forms import RecipeForm

def is_url_parsed (url: str) -> bool | str:
    is_parsed= not ParseredSites.objects.get_or_create(url = url)[1]
    return is_parsed

def get_recipe_by_url(url: str) -> dict:
    """Принимает URL и возвращает рецепт в json"""
    if is_url_parsed(url):
        pass


def take_root_from_url(recipe_url: str) -> str:
    """Получает на вход ссылку на рецепт, возвращает корень сайта"""

    # получаю чтото типо www.САЙТ.РАСШИРЕНИЕ
    clean_url = recipe_url.split("/")[2]
    return clean_url[4:]

def got_form(POST) -> None | str:
    """получает данные с формы и обрабатывет их, и только сохраняет в бд. может вернуть ошибку"""
    form_type = POST.get('form_type')
    if form_type == 'recipe':
        form = RecipeForm(POST)
        if form.is_valid():
            form.save()

        else:
            return "ОШИБКА данные заполнены не корректно"
    elif form_type == "url_recipe":
        recipe_url = POST.get("url")

        clean_url = take_root_from_url(recipe_url)
        recipe = get_recipe_by_url(clean_url)

    else:
        return ("ОШИБКА Полученная форма не существует")