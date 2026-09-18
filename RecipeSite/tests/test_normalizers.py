from pprint import pprint

from django.db.models import Model
from django.test import TestCase

from RecipeSite.admin import ParsedSiteAdmin
from RecipeSite.models import Recipe, ParseredSites
from RecipeSite.services.got_recipe import get_recipe_by_url
from RecipeSite.services.parser_manager.parser_base import RecipeGet
from RecipeSite.services.parser_manager.parsers import food_ru

class NormalizerTimeDaysHoursMinTests(TestCase):

    def test_parses_all_three_units_shortcut(self):
        result = RecipeGet._normalize_Days_Hours_Min("9 д. 5 ч. 12 м.")
        self.assertEqual(result["days"], 9)
        self.assertEqual(result["hours"], 5)
        self.assertEqual(result["minutes"], 12)

    def test_parses_all_three_units_end_words(self):
        result = RecipeGet._normalize_Days_Hours_Min("9 дебилов 5 ч сов 12 метров")
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], 5)
        self.assertEqual(result["minutes"], None)


    def test_parses_all_three_units_without_space(self):
        result = RecipeGet._normalize_Days_Hours_Min("9дней 5часов 12минут")
        self.assertEqual(result["days"], 9)
        self.assertEqual(result["hours"], 5)
        self.assertEqual(result["minutes"], 12)

    def test_parses_all_three_units(self):
        result = RecipeGet._normalize_Days_Hours_Min("9 дней 5 часов 12 минут")
        self.assertEqual(result["days"], 9)
        self.assertEqual(result["hours"], 5)
        self.assertEqual(result["minutes"], 12)

    def test_parses_days_and_minutes_without_hours(self):
        result = RecipeGet._normalize_Days_Hours_Min("9 дней 12 минут")
        self.assertEqual(result["days"], 9)
        self.assertEqual(result["hours"], None)
        self.assertEqual(result["minutes"], 12)

    def test_single_word_den_day_means_one_day(self):
        result = RecipeGet._normalize_Days_Hours_Min("день")
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["hours"], None)
        self.assertEqual(result["minutes"], None)

        # errors
    def test_raises_value_error_for_empty_string(self):
        with self.assertRaises(ValueError) as ctx:
            RecipeGet._normalize_Days_Hours_Min("")
        self.assertEqual(str(ctx.exception), "Time text cannot be empty")

    def test_raises_value_error_for_whitespace_only(self):
        with self.assertRaises(ValueError) as ctx:
            RecipeGet._normalize_Days_Hours_Min("   \n\t  ")
        self.assertEqual(str(ctx.exception), "Time text cannot be empty")



        # edge test

        # конвертирование минут
    def test_59_minutes_stays_as_minutes(self):
        result =  RecipeGet._normalize_Days_Hours_Min("59 минут")
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], None)
        self.assertEqual(result["minutes"], 59)

    def test_60_minutes_to_hour(self):
        result = RecipeGet._normalize_Days_Hours_Min("60 минут")
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], 1)
        self.assertEqual(result["minutes"], None)

    def test_61_minutes_to_hour_and_min(self):
        result = RecipeGet._normalize_Days_Hours_Min("61 минут")
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], 1)
        self.assertEqual(result["minutes"], 1)

        # кнвертирование часов
    def test_converts_hours_over_24_to_days(self):
        result =  RecipeGet._normalize_Days_Hours_Min("28 часов")
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["hours"], 4)
        self.assertEqual(result["minutes"], None)

    def test_23_hours_stays_hours(self):
        result =  RecipeGet._normalize_Days_Hours_Min("23 часа")
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], 23)
        self.assertEqual(result["minutes"], None)

    def test_24_hours_converts_day(self):
        result =  RecipeGet._normalize_Days_Hours_Min("24 часа")
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["hours"], None)
        self.assertEqual(result["minutes"], None)