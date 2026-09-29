import re
from abc import ABC, abstractmethod

import pymorphy3
import requests
from bs4 import BeautifulSoup as bs
from django.db.models import Model

from RecipeSite.models import ingredients_set, ingredient_forms, SuggestNewIngredientForms, IngredientSuggestion
from RecipeSite.services.parser_manager.parse_ingredient import IngredientParser
from RecipeSite.services.units_name import all_units


# from urllib.robotparser import normalize

class RecipeGet(ABC):
    # нормализаторы
    _normalize_Days_Hours_Min = None
    _normalize_DHM = None
    _normalize_ingredient_name_set_table = None
    _normalize_ingredient_name_form_table = None
    _normalize_ingredient_name_pymorphy2 = None

    @abstractmethod
    def __init__(self, url, user):
        self.user = user
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
    def get_title(self) -> str:
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


    def ingredient_normalize(self, ingredient: str, position: int) -> str | dict[str, str | int]:
        """получает строчку ингридиента, разюирает ее на части, нормализует имя и ед.изм"""
        parsed_ingredient = RecipeGet.ingredient_parse(ingredient, position)
        if not parsed_ingredient:
            return ingredient

        parsed_ingredient["name"] = self.normalize_ingredient_name(str(parsed_ingredient["name"]))
        parsed_ingredient["unit"] = RecipeGet.normalize_ingredient_unit(str(parsed_ingredient["unit"]))

        return parsed_ingredient

    def normalize_ingredient_name(self, ingredient_name: str) -> str:
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
            self.save_new_ingredient(ingredient_name, self.user)
            return ingredient_name

    @staticmethod
    def normalize_ingredient_unit(unit_name: str) -> str:
        # TODO: сделать нормализацию ед.изм
        pass

    @staticmethod
    def _normalize_ingredient_name_set_table(name: str) -> str | None:
        """Проверяет является ли ингриидентв начюформе - ищет в таблице ingredients_set"""
        if ingredients_set.objects.filter(name=name).exists():
            return name
        else:
            return None

    @staticmethod
    def _normalize_ingredient_name_form_table(name: str) -> str | None:
        """Проверяет является ли ингриидентв начюформе - ищет в таблице ingredients_set"""
        if ingredient_form := ingredient_forms.objects.filter(ingredient_form=name).first():
            return str(ingredient_form.ingredient_correct_form)
        else:
            return None

    @staticmethod
    def get_normalized_ingredient_and_forms(ingredient: str) -> tuple[str, list[str]]:
        # TODO: надо подумать что бы обьект создавался один раз. этого достаточно
        # TODO: то что преобразуется по отдельности не всегда получается адекватно; 'белок', 'куриный', 'яйцо', 'raw_text': 'Белок куриного яйца
        """получает имя ингридиента, переводит в начальную форму, сохраняет в бд ингридиенти формы:"""
        target_tags = [{'gent', 'sing'}, {'gent', 'plur'}]
        base_tag = {'nomn', 'sing'}

        ingredient_forms = []
        normal_gramames = []
        normal_form = []
        morph = pymorphy3.MorphAnalyzer()
        ingredient_words = re.split(r'\s-\s*|\s', ingredient)
        noun_gender = None
        ingredient_form = []

        for word in ingredient_words:
            parsed = morph.parse(word)[0]
            if 'NOUN' in parsed.tag:
                noun_gender = parsed.tag.gender
                break

        for target_tag in target_tags:
            current_tags = set(target_tag)

            for word in ingredient_words:
                ingredient_form = []
                parsed = morph.parse(word)[0]
                current_base = set(base_tag)

                if ('ADJF' in parsed.tag) and noun_gender:
                    current_base.add(noun_gender)
                inflected = parsed.inflect(current_base)
                normal_form.append(inflected.word if inflected else word)
                normal_gramames.append(parsed.tag.POS)

                if 'ADJF' in parsed.tag and 'sing' in current_tags and noun_gender:
                    current_tags.add(noun_gender)

                inflected = parsed.inflect(current_tags)

                ingredient_form.append(inflected.word if inflected else word)
            ingredient_forms.append(ingredient_form)

        if normal_gramames[0] == "ADJF" and normal_gramames[1] == "NOUN":
            normal_form[0], normal_form[1] = normal_form[1], normal_form[0]

        if len(normal_form) == 2 and ((normal_form[0] == "NOUN" and normal_form[1] == "ADJF") or (
                normal_form[0] == "ADJF" and normal_form[1] == "NOUN")):
            for ingr_index in range(len(ingredient_forms)):
                reversed_ingredient = reversed(ingredient_forms[ingr_index])
                ingredient_forms.append(" ".join(reversed_ingredient))
                ingredient_forms[ingr_index] = " ".join(ingredient_forms[ingr_index])
        else:
            for ingr_index in range(len(ingredient_forms)):
                ingredient_forms[ingr_index] = " ".join(ingredient_forms[ingr_index])

        return " ".join(normal_form), set(tuple(item) for item in ingredient_forms)

    @staticmethod
    def save_new_ingredient(ingredient, user) -> None:
        """должен сохранять новый ингридиент в отдельную таблицу, в которой я бы уже одобряла новые ингридиенты"""

        normal_form, new_ingredient_forms = GetIngredientForms(ingredient).get_normal_and_form()

        suggestion = IngredientSuggestion.objects.create(
            normal_form=normal_form,  # или ingredient_name, если переименуете
            status="pending",
            user=user
        )
        for form in new_ingredient_forms:
            SuggestNewIngredientForms.objects.create(
                ingredient_form=form,
                suggestion=suggestion,
            )


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
        parser = IngredientParser()
        result = parser.parse(ingredient)
        if result:
            result["position"] = position
            return result
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
            "hours": int(data["hours"]) if data["hours"] else None,
            "minutes": int(data["minutes"]) if data["minutes"] else None,
        }

    @staticmethod
    def _normalize_Days_Hours_Min(new_time: str) -> dict[str, int | None] | None:
        """формат 'X дни У часы Z минут', если удалось - возвращает словарик"""

        # TODO: перевести в каждую функцию парсинга отдельно (времяБ имя и тп)
        new_time = new_time.strip()
        if not new_time:
            raise ValueError("Time text cannot be empty")

        days_re = re.search(r"(?P<number>\d+)?\s*(?P<unit>дней|день|д)\b", new_time)
        hours_re = re.search(r"(?P<number>\d+)?\s*(?P<unit>часов|час|ч)\b", new_time)
        minutes_re = re.search(r"(?P<number>\d+)?\s*(?P<unit>минут|мин|м|минута)\b", new_time)

        def result_get(result, singular_form):
            if not result:
                return None

            if result.group("unit") == singular_form:
                return 1
            return int(result.group("number"))

        result = {
            "days": result_get(days_re, "день"),
            "hours": result_get(hours_re, "час"),
            "minutes": result_get(minutes_re, "минута"),
        }

        for i in result.values():
            if i is not None:
                break
        else:
            return None

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

        result["hours"], result["days"] = RecipeGet._carry_over(result["hours"], result["days"], 24)
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


class GetIngredientForms:
    morph = pymorphy3.MorphAnalyzer()
    target_tags = [{'gent', 'sing'}, {'gent', 'plur'}]
    base_tag = {'nomn', 'sing'}

    def __init__(self, ingredient):
        self.ingredient_words = re.split(r'\s*-\s*|\s', ingredient)

        self.noun_gender = None
        self._need_reverse = False
        self.normal_form = []
        self.normal_grammes = []
        self.ingredient_forms = []

        self.get_noun_gender()
        self.get_normal_form()  # здесь выставится _need_reverse
        self.get_ingredient_forms()
        self.if_abj_noun()  # добавит перевёрнутые варианты
        self.normalise_forms()

    def get_normal_and_form(self):
        return " ".join(self.normal_form), set(self.ingredient_forms)

    def get_noun_gender(self):
        for word in self.ingredient_words:
            parsed = GetIngredientForms.morph.parse(word)[0]
            if 'NOUN' in parsed.tag:
                self.noun_gender = parsed.tag.gender
                break

    def get_ingredient_forms(self):
        for target_tag in GetIngredientForms.target_tags:

            ingredient_form = []

            for word in self.ingredient_words:
                parsed = GetIngredientForms.morph.parse(word)[0]
                current_tags = set(target_tag)

                word_form, _ = self.get_form(parsed, current_tags, word)
                ingredient_form.append(word_form)

            self.ingredient_forms.append(ingredient_form)

    def is_noun_abj(self):
        # сработает и для "прил + сущ", и для "сущ + прил"
        if len(self.normal_grammes) == 2 and \
                {self.normal_grammes[0], self.normal_grammes[1]} == {"ADJF", "NOUN"}:
            self._need_reverse = True

    def get_normal_form(self):
        current_base = set(self.base_tag)
        for i, word in enumerate(self.ingredient_words):
            parsed = GetIngredientForms.morph.parse(word)[0]
            if 'ADJF' in parsed.tag and i > 0:
                self.normal_form.append(word)
                self.normal_grammes.append(parsed.tag.POS)
            else:
                normal_word, grammas = self.get_form(parsed, current_base, word)
                self.normal_form.append(normal_word)
                self.normal_grammes.append(grammas)
        self.is_noun_abj()

        if self._need_reverse and self.normal_grammes[0] == "ADJF":
            self.normal_form[0], self.normal_form[1] = self.normal_form[1], self.normal_form[0]

    def if_abj_noun(self):
        if self._need_reverse:
            self.ingredient_forms += [
                [form[1], form[0]] for form in self.ingredient_forms
            ]

    def get_form(self, parsed, base, word):

        if 'ADJF' in parsed.tag and 'sing' in base and self.noun_gender:
            base.add(self.noun_gender)
        inflected = parsed.inflect(base)
        #
        # self.normal_form.append(inflected.word if inflected else word)
        grammas = parsed.tag.POS
        return inflected.word if inflected else word, grammas

    def normalise_forms(self):
        for indr_index in range(len(self.ingredient_forms)):
            self.ingredient_forms[indr_index] = " ".join(self.ingredient_forms[indr_index])
