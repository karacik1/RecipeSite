import re

from RecipeSite.services.units_name import all_units
# # ============ ЧАСТИ РЕГУЛЯРКИ ============
NUMBER = r'\d+[,./]\d+|\d+'  # число: "200" или "1,5"
UNIT = rf'{all_units}(.)?\b'  # единица: "г", "кг"
SPACE = r'\s*'  # пробелы
NAME = r'[а-яё]+\b'  # название
SEPARATOR = r'[-.(+>:—=\s]*'  # разделители


# ============ СОБИРАЕМ ============



class IngredientParser:
    def __init__(self):
        self.parsers = [
            self._parse_num_unit_name,   # "2 кг муки (просеянной)"
            self._parse_name_num_unit,   # "муки 2 кг  (просеянной)"
            self._parse_unit_name,       # "шт лука, нарезанного"
            self._parse_name_unit,       # "лука шт"
            self._parse_name_only,       # "соль"

        ]

    def parse(self, text: str) -> dict | None:
        text = text.strip().lower()
        if not text:
            return None

        for parser in self.parsers:
            raw = parser(text)
            if raw:
                return {
                    "name": raw.get("name") or "",
                    "amount": raw.get("amount") or "",
                    "unit": raw.get("unit") or "",
                    "extra": raw.get("extra") or "",
                    "raw_text": text,
                }
        return None

    def _parse_num_unit_name(self, ingredient: str) -> dict | None:
        """'2 кг муки (просеянной)'"""
        match = re.match(
            rf'^(?P<amount>{NUMBER}){SPACE}'
            rf'(?P<unit>{UNIT})?{SPACE}'
            rf'(?P<name>{NAME})'
            rf'(?P<extra>.*)$',          # ← extra: всё после name
            ingredient
        )
        return match.groupdict() if match else None

    def _parse_name_num_unit(self, ingredient: str) -> dict | None:
        """'2 кг муки (просеянной)'"""
        match = re.match(
            rf'^(?P<name>{NAME}){SEPARATOR}'
            rf'(?P<amount>{NUMBER}){SPACE}'
            rf'(?P<unit>{UNIT})?'
            rf'(?P<extra>.*)$',          # ← extra: всё после name
            ingredient
        )
        return match.groupdict() if match else None

    def _parse_unit_name(self, ingredient: str) -> dict | None:
        """'шт лука, нарезанного'"""
        match = re.match(
            rf'^(?P<unit>{UNIT}){SPACE}'
            rf'(?P<name>{NAME})'
            rf'(?P<extra>.*)$',          # ← extra
            ingredient
        )
        return match.groupdict() if match else None

    def _parse_name_unit(self, ingredient: str) -> dict | None:
        """'лука шт'"""
        match = re.match(
            rf'^(?P<name>{NAME}){SEPARATOR}'
            rf'(?P<unit>{UNIT})'
            rf'(?P<extra>.*)$',          # ← extra
            ingredient
        )
        return match.groupdict() if match else None

    def _parse_name_only(self, ingredient: str) -> dict | None:
        """'соль'"""
        match = re.match(
            rf'^(?P<name>{NAME})'
            rf'(?P<extra>.*)$',          # ← extra
            ingredient
        )
        return match.groupdict() if match else None
