from django.test import TestCase
from .models import User, ingredients_set, ingredient_forms
from .services.parsers import RecipeGet  # Ваша функция

# в сет молоко сахар
# в форм молока молоку
class TestUserServices(TestCase):

    def setUp(self):
    #     # 1. Создаем тестовые данные (вызывается перед каждым тестом)
        moloko = ingredients_set.objects.create(name="молоко")
        ingredients_set.objects.create(name="сахар")

        ingredient_forms.objects.create(ingredient_form="молоку", ingredient_correct_form=moloko)
        ingredient_forms.objects.create(ingredient_form="молока", ingredient_correct_form = moloko)



    def test_get_active_users(self):
        self.assertEqual(RecipeGet._normalize_ingredient_name_form_table("молока"), "молоко")
