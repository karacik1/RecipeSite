import re
import time
from pprint import pprint
from pydoc import describe
from unittest import result
from urllib.robotparser import normalize
from venv import logger

import requests
from bs4 import BeautifulSoup as bs
from abc import ABC, abstractmethod
from RecipeSite import tests
from RecipeSite.models import ingredients_set, ingredient_forms
from RecipeSite.services.units_name import test, all_units


class RecipeGet(ABC):
    # нормализаторы
    _normalize_Xdays_Yhours_Zmin = None
    _normalize_XYZ = None
    _normalize_ingredient_name_set_table = None
    _normalize_ingredient_name_form_table = None
    _normalize_ingredient_name_pymorphy2 = None

    @abstractmethod
    def __init__(self, url):

        self.soup = self._make_soup(url)

        self.title = self.get_title()
        self.img_url = self.get_img_url()
        self.ingredients = self.get_ingredients()
        self.cooking_time = self.get_cooking_time()
        self.steps = self.get_steps()

        self.normalizer()

    def normalizer(self):
        if self.cooking_time:
            self.cooking_time = self.normalize_time(self.cooking_time)

    @abstractmethod
    def get_ingredients(self):
        return

    def get_cooking_time(self):
        return

    @abstractmethod
    def get_title(self):
        return

    @abstractmethod
    def get_steps(self):
        return

    def get_img_url(self):
        return

    def _make_soup(self, url):
        site = requests.get(url)
        soup = bs(site.text, "html.parser")
        soup.prettify()
        return soup

    def get_recipe(self):
        return {
            "title": self.title,
            "cooking_time": self.cooking_time,
            "img_url": self.img_url,
            "ingredients": self.ingredients,
            "steps": self.steps,
            }

    def normalize_time(self, time_string: str) -> str:

        normalizers = [RecipeGet._normalize_Xdays_Yhours_Zmin, RecipeGet._normalize_XYZ]
        for normalizer in normalizers:
            if result := normalizer(time_string):
                parts = []

                # Безопасно извлекаем значения
                days = result.get("days", 0)
                hours = result.get("hours", 0)
                minutes = result.get("minutes", 0)

                if days:
                    parts.append(f"{days} д.")
                if hours:
                    parts.append(f"{hours} ч.")
                if minutes:
                    parts.append(f"{minutes} мин.")

                if parts:
                    return " ".join(parts)

        print("\033[91mВремя имеет не обработанный формат\033[0m")
        return time_string
    @staticmethod
    def ingredient_normalize(ingredient: str) -> str:
        """получает строчку ингридиента, разюирает ее на части, нормализует имя и ед.изм"""
        parsed_ingredient = RecipeGet.ingredient_parse(ingredient)
        if not parsed_ingredient:
            return ingredient

        normalized_ingredient = RecipeGet.normalize_ingredient_name_units(parsed_ingredient["name"],parsed_ingredient["unit"])
        return normalized_ingredient

    @staticmethod
    def normalize_ingredient_name_units(ingredient_name: str | None = None, ingredient_unit: str | None = None) -> dict[str, str |None]:
        """Нормализует название ингридиента и название ед.изм."""
        normalizers = [RecipeGet._normalize_ingredient_name_set_table,
                       RecipeGet._normalize_ingredient_name_form_table,
                       RecipeGet.normalize_ingredient_name_pymorphy2]
        for normalizer in normalizers:
            if normalized_name := normalizer(ingredient_name):
                break
        else: normalized_name = "\033[32m НЕ УДАЛОСЬ НОРМАЛИЗОВАТЬ\033[0m"

        normalized_unit = ingredient_unit
        return {
            "name": normalized_name,
            "unit": normalized_unit
        }
    @staticmethod
    def _normalize_ingredient_name_set_table(name: str) -> str | None:
        """Проверяет является ли ингриидентв начюформе - ищет в таблице ingredients_set"""
        if ingredients_set.objects.filter(name = name).exists():
            return name
        else: return None

    @staticmethod
    def _normalize_ingredient_name_form_table(name: str) -> str | None:
        """Проверяет является ли ингриидентв начюформе - ищет в таблице ingredients_set"""
        if ingredient_form := ingredient_forms.objects.filter(ingredient_form=name).first():
            return str(ingredient_form.ingredient_correct_form)
        else:
            return None

    def normalize_ingredient_name_pymorphy2(name: str) -> str:
        """получает имя ингридиента, переводит в начальную форму, сохраняет в бд ингридиенти формы:"""
        pass


    @staticmethod
    def ingredient_parse(ingredient: str) -> dict[str, str] | None:
        """разбирает ингридиент на четыре части: название,еденицы измерения, количество, дополнение"""
        pattern = re.compile(
            pattern=re.compile(
                rf'(?:(?P<qty_before>\d+[,./]\d+|\d+)\s*)?'
                rf'(?:(?P<unit_before>{all_units})[-.\(+>:—=\s]*\b\s*)?'
                rf'(?P<name>[-а-яё\s]+?(?=[-:—]*\s*\d|\s*(?:{all_units})\b|$))'
                rf'(?:[-.(+>:—=\s]*(?P<qty_after>\d+[,./]\d+|\d+)?\s*)?'
                rf'(?:(?P<unit_after>{all_units})\b)?'
                rf'(?P<rest>.*)'
            )
        )

        parsed_ingredient = pattern.fullmatch(ingredient.strip().lower())
        if parsed_ingredient:
            ingredients = parsed_ingredient.groupdict()

            ingradient_count = str(ingredients["qty_before"] or ingredients["qty_after"] or "")
            ingradient_unit = str(ingredients["unit_before"] or ingredients["unit_after"] or "")
            addition = str(ingredients["rest"] or "")
            ingradient_name = str(ingredients["name"] or "")
            return {
                "name": ingradient_name,
                "count": ingradient_count,
                "unit": ingradient_unit,

                "addition": addition,
            }
        else:
            return None

    @staticmethod
    def _normalize_XYZ(new_time: str) -> dict[str, int | None]:
        """формат 'X:Y:Z', если удалось - возвращает словарик"""
        time = {
            "days": None,
            "hours": None,
            "minutes": None,
        }

        data_type = new_time.count(":")

        match data_type:
            case 0:
                time["minutes"] = int(new_time)
            case 1:
                hour_minutes = re.search(r"(\d+)\s*:\s*(\d+)", new_time)
                time["hours"] = int(hour_minutes.group(1))
                time["minutes"] = int(hour_minutes.group(2))
            case 3:
                days_hour_minutes = re.search(r"(\d+)\s*:\s*(\d+):\s*(\d+)", new_time)
                time["days"] = int(days_hour_minutes.group(1))
                time["hours"] = int(days_hour_minutes.group(2))
                time["minutes"] = int(days_hour_minutes.group(3))

        return time

    @staticmethod
    def _normalize_Xdays_Yhours_Zmin(new_time: str) -> dict[str, int | None]:
        """формат 'X дни У часы Z минут', если удалось - возвращает словарик"""

        days_re = re.search(r"(\d+)\s*(дней|день|д)", new_time)
        hours_re = re.search(r"(\d+)\s*(часов|час|ч)", new_time)
        minutes_re = re.search(r"(\d+)\s*(минут|мин|м|минута)", new_time)

        days = int(days_re.group(1)) if days_re else None
        hours = int(hours_re.group(1)) if hours_re else None
        minutes = int(minutes_re.group(1)) if minutes_re else None

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
        }


class rusfosianfood_com(RecipeGet):
    def __init__(self, url):
        super().__init__(url)

    def get_title(self):
        return self.soup.find("h1", class_="title").string

    def get_steps(self):
        try1 = self.soup.find("div", class_="step_images_n")
        if try1:
            return list(try1.stripped_strings)

        try2 =  self.soup.find("div", id="how")
        if try2:
            return list(try2.stripped_strings)
        return None

    def get_ingredients(self):
        return list(self.soup.find("table", class_="ingr").stripped_strings)[2:]

    def get_cooking_time(self):
        spend_time = self.soup.find_all("span", class_="hl")

        # проверяет наличие потраченного времени, но всегда существует количество порций
        if len(spend_time)>1:
            spend_time=spend_time[1]
            time = [b.string for b in spend_time.find_all("b")]
            time = ":".join(time)
            return time
        return None
    def get_img_url(self):
        teg = self.soup.find("a", class_="tozoom").get("href")
        absolut_url = "https:"+teg
        return absolut_url

class food_ru(RecipeGet):
    def __init__(self, url):
        super().__init__(url)
    def get_ingredients(self):
        ingredients = []
        table = self.soup.find_all("tr", class_="ingredient")
        for row in table:
            ingredients.append(" ".join(row.stripped_strings))
        return  ingredients

    def get_steps(self):
        steps = self.soup.find("section", id="step-by-step-recipe").stripped_strings
        pure_steps = filter(lambda x: x.isdigit()==False and x != "Шаг" and x!="произвести впечатление", list(steps))
        return list(pure_steps)[2:]

    def get_title(self):
        title = self.soup.find("h1", class_="title_main__ok7t1").string
        return title

    def get_cooking_time(self):
        time = self.soup.find("dd", class_="properties_definition__eBeO3 properties_value__kAeD9 properties_valueWithIcon__WDXDm duration").text
        return time
    def get_img_url(self):
        teg =  self.soup.find( "img", attrs= {"fetchpriority":"high"})
        url = teg.get("src")
        return url



