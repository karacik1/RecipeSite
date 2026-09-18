from pprint import pprint
from unittest import result

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
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 5)
        self.assertIsNone(result["minutes"])


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
        self.assertIsNone(result["hours"])
        self.assertEqual(result["minutes"], 12)

    def test_single_word_den_day_means_one_day(self):
        result = RecipeGet._normalize_Days_Hours_Min("день")
        self.assertEqual(result["days"], 1)
        self.assertIsNone(result["hours"])
        self.assertIsNone(result["minutes"])

        # errors
    def test_raises_value_error_for_empty_string(self):
        with self.assertRaises(ValueError) as ctx:
            RecipeGet._normalize_Days_Hours_Min("")
        self.assertEqual(str(ctx.exception), "Time text cannot be empty")

    def test_raises_value_error_for_whitespace_only(self):
        with self.assertRaises(ValueError) as ctx:
            RecipeGet._normalize_Days_Hours_Min("   \n\t  ")
        self.assertEqual(str(ctx.exception), "Time text cannot be empty")

class ConvertTimeFromOver(TestCase):
    def test_converts_all_three_units(self):
        result = RecipeGet.conver_to_normal_form({
            "days": 1,
            "hours": 25,
            "minutes": 61,
        })
        self.assertEqual(result["days"], 2)
        self.assertEqual(result["hours"], 2)
        self.assertEqual(result["minutes"], 1)

    def test_converts_only_days_multiple_of_24(self):
        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": 72,
            "minutes": None,
        })
        self.assertEqual(result["days"], 3)
        self.assertEqual(result["hours"], None)
        self.assertEqual(result["minutes"], None)

    def test_converts_only_minutes_multiple_of_60(self):
        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": None,
            "minutes": 180,
        })
        self.assertEqual(result["days"], None)
        self.assertEqual(result["hours"], 3)
        self.assertEqual(result["minutes"], None)


        # edge test
        # конвертирование минут
    def test_59_minutes_stays_as_minutes(self):
        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": None,
            "minutes": 59,
        })
        self.assertIsNone(result["days"])
        self.assertIsNone(result["hours"])
        self.assertEqual(result["minutes"], 59)

    def test_60_minutes_to_hour(self):

        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": None,
            "minutes": 60,
        })
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 1)
        self.assertIsNone(result["minutes"])

    def test_61_minutes_to_hour_and_min(self):

        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": None,
            "minutes": 61,
        })
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 1)
        self.assertEqual(result["minutes"], 1)

        # кнвертирование часов
    def test_converts_hours_over_24_to_days(self):

        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": 28,
            "minutes": None,
        })
        self.assertEqual(result["days"], 1)
        self.assertEqual(result["hours"], 4)
        self.assertIsNone(result["minutes"])

    def test_23_hours_stays_hours(self):

        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": 23,
            "minutes": None,
        })
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 23)
        self.assertIsNone(result["minutes"])

    def test_test_24_hours_converts_day(self):

        result = RecipeGet.conver_to_normal_form({
            "days": None,
            "hours": 24,
            "minutes": None,
        })
        self.assertEqual(result["days"], 1)
        self.assertIsNone(result["hours"])
        self.assertIsNone(result["minutes"])

    def test_not_converts_over_days(self):

        result = RecipeGet.conver_to_normal_form({
            "days": 1000,
            "hours": None,
            "minutes": None,
        })
        self.assertEqual(result["days"], 1000)
        self.assertIsNone(result["hours"])
        
        self.assertIsNone(result["minutes"])
class NormalizerDHMTests(TestCase):

    def test_hours_minutes(self):
        result = RecipeGet._normalize_DHM("12:20")
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 12)
        self.assertEqual(result["minutes"], 20)

    def test_only_minutes(self):
        result = RecipeGet._normalize_DHM("12")
        self.assertIsNone(result["days"])
        self.assertIsNone(result["hours"])
        self.assertEqual(result["minutes"], 12)


    def test_hours_minutes_and_one_space(self):
        result = RecipeGet._normalize_DHM("12: 20")
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 12)
        self.assertEqual(result["minutes"], 20)

    def test_hours_minutes_and_minus_sep(self):
        result = RecipeGet._normalize_DHM("12-20")
        self.assertIsNone(result["days"])
        self.assertEqual(result["hours"], 12)
        self.assertEqual(result["minutes"], 20)


