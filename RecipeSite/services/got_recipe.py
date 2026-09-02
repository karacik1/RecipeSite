from _pyrepl import console

from urllib import request
from django.shortcuts import get_object_or_404
from unicodedata import category
from RecipeSite.models import Category, Recipe, ParseredSites, ingredients_set, RecipeIngredient
from RecipeSite.forms import RecipeForm
from RecipeSite.services.parser_manager import parsers
from RecipeSite.services.parser_manager.parsers import Parsers_list


def is_site_parsed (recipe_url: str) -> str:
    """Проверяет парсили ли уже сайт или нет.
    Если сайт парсили - то будет метод. если нет - пустая строчка"""
    site_root = get_root_from_url(recipe_url)

    site, is_created = ParseredSites.objects.get_or_create(url = site_root)
    print(site.parser_name)
    return site.parser_name

def is_recipe_exists(url: str) -> bool:
    """Проверяет наличие рецепта в бд"""
    return Recipe.objects.filter(original_URL = url).exists()

def use_AI(url: str) -> bool | str:
    """пишет промт и возвращает рецепт, также сохраняет адресс сайта в бд,, для будущего парсинга"""
    #TODO: нужна обработка url иишкой
    pass

def save_recipe(recipe, ) -> None:
    """сохраняет рецепт в бд"""
    # TODO: может можно сделать адекватнее присваивание. добавить img_url

    new_recipe = Recipe.objects.create(
        title = recipe["title"],
        category = None,
        cooking_time = recipe["cooking_time"],
        description = recipe["steps"],
        original_URL = recipe["original_URL"],
        # user = None,
    )

    # TODO: ингридиенты должны быть уже записаны в сет
        # КОГДА СДЕЛАЮ НОРМАЛЬНЫЙ JSON
        # RecipeIngredient.objects.create(
        #     reciep = new_recipe,
        #     ingredient = ingr,
        #     amount = ingr["amount"],
        #     extra = ingr["extra"],
        #     raw_text = ingr["raw_text"],
        #
        # )

def get_recipe_by_url(url: str) -> dict:
    """Принимает URL и возвращает рецепт в json"""
    # TODO: сделать адекватные вызовы

    if is_recipe_exists(url):
        recipe = Recipe.objects.filter(original_URL=url)
    elif parsed_site := is_site_parsed(url):
        parser = Parsers_list[parsed_site]
        recipe = parser(url).get_recipe()
        print("im here", recipe)
        # TODO: хочу что бы человек имел возможность подредактирвоать
        #  рецепт под себя, а сохранялся оригинал и модифицированный как рецепт пользователя

        save_recipe(recipe )
    else:
        recipe = use_AI(url)
        recipe = None
    print("ПОЛУЧЕННЫЙ РЕЦЕПТ:", recipe)



def get_root_from_url(recipe_url: str) -> str:
    """Получает на вход ссылку на рецепт, возвращает корень сайта"""

    # получаю чтото типо www.САЙТ.РАСШИРЕНИЕ
    # TODO: сделать что бы www не было
    #  Идеальное совпадение: Пользователи могут вводить ссылки по-разному:
    #  один скопирует https://food.ru, другой — http://food.ru, а третий вообще food.ru/recipe/1.
    clean_url = recipe_url.split("/")[2]
    return clean_url

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

        recipe = get_recipe_by_url(recipe_url)

    else:
        return ("ОШИБКА Полученная форма не существует")