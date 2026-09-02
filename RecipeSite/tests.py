from pprint import pprint

from django.db.models import Model
from django.test import TestCase

from RecipeSite.admin import ParsedSiteAdmin
from RecipeSite.models import Recipe, ParseredSites
from RecipeSite.services.got_recipe import get_recipe_by_url
from RecipeSite.services.parser_manager.parsers import food_ru


# в сет молоко сахар
# в форм молока молоку
class ParseFoodRu(TestCase):

    def setUp(self):
        ParseredSites.objects.get_or_create(url = "food.ru", parser_name="food_ru")

    def test_get_active_users(self):
        url = "https://food.ru/recipes/182769-merengovyi-rulet-1691818518"
        pprint(food_ru(url).get_recipe())
        get_recipe_by_url(url)
        pprint(Recipe.objects.all())
