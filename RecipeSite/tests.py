from pprint import pprint

from django.test import TestCase

from RecipeSite.services.parser_manager.parsers import food_ru


# в сет молоко сахар
# в форм молока молоку
class TestUserServices(TestCase):

    def setUp(self):
        pass
    #     # 1. Создаем тестовые данные (вызывается перед каждым тестом)
    #     moloko = ingredients_set.objects.create(name="молоко")
    #     ingredients_set.objects.create(name="сахар")

        # ingredient_forms.objects.create(ingredient_form="молоку", ingredient_correct_form=moloko)
        # ingredient_forms.objects.create(ingredient_form="молока", ingredient_correct_form = moloko)



    def test_get_active_users(self):
        url = "https://food.ru/recipes/182769-merengovyi-rulet-1691818518"
        recipe = food_ru(url).get_recipe()
        pprint(recipe)
