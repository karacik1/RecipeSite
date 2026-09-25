import pytest
from _pytest import subtests
from django.test import TestCase
from RecipeSite.services.parser_manager.parser_base import RecipeGet, GetIngredientForms


class TestIngredientParser:
    """Все юнит-тесты, связанные только с парсингом текста"""

    def test_parse_simple_name_unit_amount(self, recipe_get, simple_name_unit_amount):
        ingredient, correct_result = simple_name_unit_amount
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_ingredient_unit_amount_name(self, recipe_get, ingredient_unit_amount_name):
    
        ingredient, correct_result = ingredient_unit_amount_name
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_without_amount(self, recipe_get, without_amount):
    
        ingredient, correct_result = without_amount
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_amount_is_fractions(self, recipe_get, amount_is_fractions):
    
        ingredient, correct_result =  amount_is_fractions
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_with_special_sep(self, recipe_get, with_special_sep):
    
        ingredient, correct_result = with_special_sep
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_special_unit(self, recipe_get, special_unit):
        ingredient, correct_result = special_unit
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    
    def test_parse_duble_unit_name(self, recipe_get, duble_unit_nam):
        ingredient, correct_result = duble_unit_nam
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_only_name(self, recipe_get, only_name):
        ingredient, correct_result = only_name
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result
    
    def test_parse_unit_amount_unit_rest(self, recipe_get, unit_amount_unit_rest):
        ingredient, correct_result =  unit_amount_unit_rest
        result = recipe_get.ingredient_parse(str(ingredient), 1)
        assert result == correct_result

class TestIngredientNormalization:

    def test_noun_normal_form(self):
        """Исходное слово в начальной форме ('яблоко')"""
        actual_normal, actual_forms = GetIngredientForms("яблоко").get_normal_and_form()
        assert actual_normal == "яблоко"
        assert actual_forms == {"яблока", "яблок"}

    def test_noun_no_normal_form(self):
        """Исходное слово в родительном падеже ('яблока')"""
        actual_normal, actual_forms = GetIngredientForms("яблоку").get_normal_and_form()
        assert actual_normal == "яблоко"
        assert actual_forms == {"яблока", "яблок"}

    def test_double_noun_name_space(self):
        """Словосочетание разделено пробелом ('какао порошок')"""
        actual_normal, actual_forms = GetIngredientForms("какао порошок").get_normal_and_form()
        assert actual_normal == "какао порошок"
        assert actual_forms == {"какао порошка", "какао порошков"}

    def test_double_noun_name_minus(self):
        """Слово пишется через дефис без пробелов ('какао-порошок')"""
        actual_normal, actual_forms = GetIngredientForms("какао-порошок").get_normal_and_form()
        assert actual_normal == "какао порошок"
        assert actual_forms == {"какао порошка", "какао порошков"}

    def test_double_noun_name_minus_space(self):
        """Слово пишется через дефис с пробелами вокруг (' какао - порошок ')"""
        actual_normal, actual_forms = GetIngredientForms("какао - порошок").get_normal_and_form()
        assert actual_normal == "какао порошок"
        assert actual_forms == {"какао порошка", "какао порошков"}

    def test_abj_noun(self):
        """Прилагательное перед существительным ('льняное масло')"""
        actual_normal, actual_forms = GetIngredientForms("льняное масло").get_normal_and_form()
        assert actual_normal == "масло льняное"
        assert actual_forms == {"льняного масла", "льняных масел", "масла льняного", "масел льняных"}

    def test_noun_abj(self):
        """Существительное перед прилагательным ('масло льняное')"""
        actual_normal, actual_forms = GetIngredientForms("масло льняное").get_normal_and_form()
        assert actual_normal == "масло льняное"
        assert actual_forms == {"льняного масла", "льняных масел", "масла льняного", "масел льняных"}



