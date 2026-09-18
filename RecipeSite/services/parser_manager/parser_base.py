import datetime
import re
from abc import ABC, abstractmethod
from collections import namedtuple
from urllib.robotparser import normalize

import pymorphy3
import requests
from bs4 import BeautifulSoup as bs
from django.template.defaultfilters import date

from RecipeSite.models import ingredients_set, ingredient_forms
from RecipeSite.services.units_name import all_units
from datetime import datetime
# from urllib.robotparser import normalize

class RecipeGet(ABC):
    # нормализаторы
    _normalize_Days_Hours_Min = None
    _normalize_DHM = None
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
    def get_ingredients(self) -> dict[str, str | int]:
        """
        :return: list состоящих из Dict: Словарь с рецептом, содержащий поля:
                    - 'name' (str): Имя.
                    - 'amount' (str): Количество.
                    - 'unit' (str): Ед измерения.
                    - 'extra' (str): То,что не получилось парсить (обычно дополние написанное к рецепту).
                    - 'raw_text' (str): Оригинальный текст ингридиента.
                    - 'position' (int): Позиция ингридиента в списке.
        """
        pass

    def get_cooking_time(self) -> str:
        """
        :return: str - строка разного формата связанная со временем приготовления
        """
        pass

    @abstractmethod
    def get_title(self)-> str:
        """
        :return: название ингридиента
        """
        pass

    @abstractmethod
    def get_steps(self) -> list[str]:
        """
        :return: list где каждый шаг - отдельно
        """
        pass

    def get_img_url(self) -> str:
        """
        :return: возвращает url адрес картинки с оригинального рецепта
        """
        pass

    def _make_soup(self, original_URL):
        """
        :param original_URL: адресс сайта который будут парсить
        :return: специальный обьект Soup который представляет полученный сайт, разбитый по тегам
        """
        self.original_URL = original_URL
        site = requests.get(original_URL)
        soup = bs(site.text, "html.parser")
        soup.prettify()
        return soup

    def get_recipe(self) -> dict[str, str | dict[str, str | int] | list[str]]:
        """
        return:
            -'title' (str): Название рецепта.
            -'cooking_time': Время приготовления.
            -'img_url' (str): Ссыдка на изображение рецепта.
            -'ingredients' (dict):
                    'name' (str): Название ингридиента.
                    'amount' (str): Количество.
                    'unit' (str): Ед измерения.
                    'extra' (str): То,что не получилось парсить (обычно дополние написанное к рецепту).
                    'raw_text' (str): Оригинальный текст ингридиента.
                    'position' (int): Позиция ингридиента в списке.
            - 'steps' (list[str]): Шаги приготовления
            - 'original_url' (str): Ссылка на оригинал рецепта.
        """
        return {
            "title": self.title,
            "cooking_time": self.cooking_time,
            "img_url": self.img_url,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "original_URL": self.original_URL}

    def normalize_time(self, time_string: str) -> str | None:
        """
        :param time_string: получает строку содержащаю время. Обрабатывает два вида :
            1. Х дней Y часов Z минут
            2. X:Y:Z
        :return: строка формата 'X д. Y ч. Z мин.'
        : raises ValueError: если строка имеет не обработанный тип
        """
        normalizers = [RecipeGet._normalize_Days_Hours_Min, RecipeGet._normalize_DHM]
        for normalizer in normalizers:
            if data := normalizer(time_string):

                result = RecipeGet.conver_to_normal_form(data)
                parts = []

                if result["days"]:
                    parts.append(f"{result["days"]} д.")
                if result["hours"]:
                    parts.append(f"{result["hours"]} ч.")
                if result["minutes"]:
                    parts.append(f"{result["minutes"]} мин.")

                if parts:
                    return " ".join(parts)
        raise ValueError("ДАННЫЙ ФОРМАТ ВРЕМЕНИ НЕ ПОДДЕРЖИВАЕТСЯ: ", time_string)

    @staticmethod
    def ingredient_normalize(ingredient: str, position: int) -> str | dict[str, str | int]:
        """получает строчку ингридиента, разюирает ее на части, нормализует имя и ед.изм"""
        parsed_ingredient = RecipeGet.ingredient_parse(ingredient, position)
        if not parsed_ingredient:
            return ingredient

        parsed_ingredient["name"]= RecipeGet.normalize_ingredient_name(str(parsed_ingredient["name"]))
        parsed_ingredient["unit"] = RecipeGet.normalize_ingredient_unit(str(parsed_ingredient["unit"]))

        return parsed_ingredient


    @staticmethod
    def normalize_ingredient_name(ingredient_name: str) -> str :
        """
        переводит разные формы ингридиента в нормальную, используя бд

        :param ingredient_name: имя ингридиента
        :return: пытается нормализовать ингридиент в соответствии с таблицей, иначе - возвращает то же
        """
        normalizers = [RecipeGet._normalize_ingredient_name_set_table,
                       RecipeGet._normalize_ingredient_name_form_table,
                       ]
        for normalizer in normalizers:
            if normalized_name := normalizer(ingredient_name):
                return normalized_name
        else:
            return ingredient_name


    @staticmethod
    def normalize_ingredient_unit(unit_name: str) -> str :
        pass

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

    @staticmethod
    def normalize_ingredient_name_pymorphy2(ingredient: str) -> list[str] | None:
        # TODO: надо подумать что бы обьект создавался один раз. этого достаточно
        # TODO: то что преобразуется по отдельности не всегда получается адекватно; 'белок', 'куриный', 'яйцо', 'raw_text': 'Белок куриного яйца
        """получает имя ингридиента, переводит в начальную форму, сохраняет в бд ингридиенти формы:"""
        morph = pymorphy3.MorphAnalyzer()
        ingredient_words = re.split(r'\s-\s*|\s', ingredient)
        normalized_ingredient = []
        for word in ingredient_words:
            p = morph.parse(word)
            for variant in p:
                # если выбранное слово: сущ, прилагательное полное или краткое
                if "NOUN" in variant.tag or "ADJF" in variant.tag or "ADJS" in variant.tag:
                    normalized_word = variant.normal_form
                    normalized_ingredient.append(normalized_word)

                    # сохраняет в бд предложений новый ингридиент
                    RecipeGet.save_new_ingredient(variant)
                    break
        return normalized_ingredient


    @staticmethod
    def save_new_ingredient(ingredient) -> None:
        """должен сохранять новый ингридиент в отдельную таблицу, в которой я бы уже одобряла новые ингридиенты"""
        pass
        # normalized_ingredient = ingredient.normal_form
        # saved_ingredient = ingredients_set.objects.create(name=normalized_ingredient)
        #
        # for form in ingredient.lexeme:
        #     word_form = form.word
        #     if word_form != normalized_ingredient and not ingredient_forms.objects.filter(ingredient_form=word_form).exists():
        #         ingredient_forms.objects.create(ingredient_form=word_form,
        #                                         ingredient_correct_form=saved_ingredient)



    @staticmethod
    def ingredient_parse(ingredient: str, position: int) -> dict[str, str | int] | None:
        """Создает словарь рецепта.

            Returns:
                Dict: Словарь с рецептом, содержащий поля:
                    - 'name' (str): Имя.
                    - 'amount' (str): Количество.
                    - 'unit' (str): Ед измерения.
                    - 'extra' (str): То,что не получилось парсить (обычно дополние написанное к рецепту).
                    - 'raw_text' (str): Оригинальный текст ингридиента.
                    - 'position' (int): Позиция ингридиента в списке.
        """
        pattern = re.compile(
            # TODO: ошибки: ["Сливки 33% жирности","Лимонный сок 1 ч. л.","Малина 200 г", "кукурузный крахмал"]
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

            ingradient_amount = str(ingredients["qty_before"] or ingredients["qty_after"] or "")
            ingradient_unit = str(ingredients["unit_before"] or ingredients["unit_after"] or "")
            extra = str(ingredients["rest"] or "")
            ingradient_name = str(ingredients["name"] or "")
            return {
                "name": ingradient_name,
                "amount": ingradient_amount,
                "unit": ingradient_unit,
                "extra": extra,
                "raw_text": ingredient,
                "position": position,
            }
        else:
            # TODO: решить чтото с тем если будет None
            return None

    @staticmethod
    # TODO: убрать в минутах None вообще
    def _normalize_DHM(new_time: str) -> dict[str, int | None] | None:
        """Формат 'Hours:Minutes' или просто 'Minutes'."""
        pattern = re.compile(
            rf'(?:(?P<hours>\d*)?\s*[:-])?\s*(?P<minutes>\d+)'
        )
        match = pattern.match(new_time.strip())

        if not match:
            return None

            # 2. Достаем данные из групп
        data = match.groupdict()

        # Предполагаем, что дней в этой строке изначально нет (всегда None)
        return {
            "days": None,
            "hours":  int(data["hours"]) if data["hours"] else None,
            "minutes":  int(data["minutes"]) if data["minutes"] else None,
        }


    @staticmethod
    def _normalize_Days_Hours_Min(new_time: str) -> dict[str, int | None]:
        """формат 'X дни У часы Z минут', если удалось - возвращает словарик"""
        new_time = new_time.strip()
        if not new_time:
            raise ValueError("Time text cannot be empty")


        days_re = re.search(r"(\d+)\s*(дней|день|д)\b", new_time)
        hours_re = re.search(r"(\d+)\s*(часов|час|ч)\b", new_time)
        minutes_re = re.search(r"(\d+)\s*(минут|мин|м|минута)\b", new_time)

        days = int(days_re.group(1)) if days_re else None
        hours = int(hours_re.group(1)) if hours_re else None
        minutes = int(minutes_re.group(1)) if minutes_re else None

        result = {
            "days": days,
            "hours": hours,
            "minutes": minutes,
        }


        return result

    @staticmethod
    def conver_to_normal_form(data: dict[str, int | None]) -> dict[str, int | None]:
        """
        конвертирует неправильне типы по виду 123ч часа, 67 минути тп.

        :param data: словарь, содержащий "days","hours", "minutes"
        :return: нормализованный словарь
        """
        result = dict(data)

        result["minutes"], result["hours"] = RecipeGet._carry_over(result["minutes"], result["hours"], 60)

        result["hours"], result["days"] = RecipeGet._carry_over( result["hours"], result["days"],24)
        return result

    @staticmethod
    def _carry_over(low_unit: int | None, high_unit: int | None, over_at: int | None):
        if low_unit is None or low_unit < over_at:
            return low_unit, high_unit

        carry = low_unit // over_at

        if high_unit is not None:
            high_unit += carry
        else:
            high_unit = carry

        low_unit %= over_at
        if low_unit == 0:
            low_unit = None

        return low_unit, high_unit