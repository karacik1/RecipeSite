units = {
    # Граммы
    'г': ['г', 'гр', 'грамм', 'грамма', 'граммов', 'граммы'],

    # Килограммы
    'кг': ['кг', 'килограмм', 'килограмма', 'килограммов', 'кило'],

    # Миллилитры
    'мл': ['мл', 'миллилитр', 'миллилитра', 'миллилитров'],

    # Литры
    'л': ['л', 'литр', 'литра', 'литров'],

    # Столовые ложки
    'ст.л.': ['ст.л.', 'ст л', 'столовая ложка', 'столовые ложки', 'столовых ложек'],

    # Чайные ложки
    'ч.л.': ['ч.л.', 'ч л', 'чайная ложка', 'чайные ложки', 'чайных ложек'],

    # Стаканы
    'стакан': ['стакан', 'стакана', 'стаканов', 'ст.', 'ст'],

    # Штуки
    'шт': ['шт', 'штук', 'штуки', 'штука'],

    # Унции (для западных рецептов)
    'oz': ['oz', 'унция', 'унции', 'унций', 'ounce', 'ounces'],

    # Фунты
    'lb': ['lb', 'фунт', 'фунта', 'фунтов', 'pound', 'pounds'],

    # Чайные ложки (англ)
    'tsp': ['tsp', 'ч.л.', 'teaspoon', 'teaspoons'],

    # Столовые ложки (англ)
    'tbsp': ['tbsp', 'ст.л.', 'tablespoon', 'tablespoons'],

    # Чашки (американские)
    'cup': ['cup', 'cups', 'чашка', 'чашки', 'чашек'],

    # Щепотка
    'щепотка': ['щепотка', 'щепотки', 'щепоток', 'щеп.'],

    # По вкусу
    'по вкусу': ['по вкусу', 'по желанию', 'по необходимости'],

    # Капли
    'капли': ['капля', 'капли', 'капель', 'кап.'],

    # Зубчики (чеснок)
    'зубчик': ['зубчик', 'зубчика', 'зубчиков', 'зуб.'],

    # Горсть
    'горсть': ['горсть', 'горсти', 'горстей'],

    # Пучок
    'пучок': ['пучок', 'пучка', 'пучков'],
}

# Плоский список для быстрого поиска
all_units_flat = [
    # Граммы
    'г', 'гр', 'грамм', 'грамма', 'граммов', 'граммы',

    # Килограммы
    'кг', 'килограмм', 'килограмма', 'килограммов', 'кило',

    # Миллилитры
    'мл', 'миллилитр', 'миллилитра', 'миллилитров',

    # Литры
    'л', 'литр', 'литра', 'литров',

    # Ложки
    'ст.л.',"ст. л.",'ст. л.','ст . л . ', 'ст л', 'столовая ложка', 'столовые ложки', 'столовых ложек',
    'ч.л.','ч. л.','ч . л .', 'ч л', 'чайная ложка', 'чайные ложки', 'чайных ложек',

    # Стаканы
    'стакан', 'стакана', 'стаканов', 'ст.', 'ст',

    # Штуки
    'шт', 'штук', 'штуки', 'штука',

    # Унции
    'oz', 'унция', 'унции', 'унций', 'ounce', 'ounces',

    # Фунты
    'lb', 'фунт', 'фунта', 'фунтов', 'pound', 'pounds',

    # Английские ложки
    'tsp', 'teaspoon', 'teaspoons',
    'tbsp', 'tablespoon', 'tablespoons',

    # Чашки
    'cup', 'cups', 'чашка', 'чашки', 'чашек',

    # Прочее
    'щепотка', 'щепотки', 'щепоток', 'щеп.',
    'по вкусу', 'по желанию', "для украшения",
    'капля', 'капли', 'капель', 'кап.',
    'зубчик', 'зубчика', 'зубчиков', 'зуб.',
    'горсть', 'горсти', 'горстей',
    'пучок', 'пучка', 'пучков',
]

# Регулярка для поиска единиц в тексте (сортировка по длине для корректного поиска)
units_for_regex = sorted(all_units_flat, key=len, reverse=True)
# Экранируем только те символы, которые могут сломать регулярное выражение
def manual_escape(text):
    # Список основных спецсимволов регулярных выражений
    for char in r".^$*+?{}[]\|()":
        text = text.replace(char, "\\" + char)
    return text

# Собираем строку без использования модуля re
all_units = "|".join(manual_escape(unit) for unit in units_for_regex) + r"\.?"

# all_units = "|".join(map(re.escape, units_for_regex))+"\\.?" здесь старая
# версия строки выше с ре. если не работает вверх - попробовать эту

test = {
    "с числами вконце": ["лука 2 шт", "мука 10гр", "молоко мл"],#
    "с числами вначале": ["2 шт лука", "500 г муки", "200 мл молока"," шт лука"],#
    "с дробями": ["1/2 стакана воды", "3/4 ч.л. соли",],
    "с тире": ["морковь - 2 шт", "яйца — 3 шт", "сахар - 100 г"],
    "с двоеточием": ["мука: 500 г", "молоко: 200 мл"],
    "без единиц": ["соль по вкусу", "зелень для украшения", "перец"],
    "с сокращениями": ["2 ст. л. масла", "1 ч. л. соды", "500 гр фарша"],
    "без пробелов": ["2шт яйца - свежие", "500г муки", "1ст.л. масла"],
    "special": ["картошка 2 шт. = 240 г", "банан - 400 г (2 шт.)", "мука - 20гр + 13гр на стол", "молоко мл","шт лука" ],

}
results_test= [
    {'qty_before': None, 'unit_before': None, 'name': 'лука', 'qty_after': '2', 'unit_after': 'шт', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'мука', 'qty_after': '10', 'unit_after': 'гр', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'молоко', 'qty_after': None, 'unit_after': 'мл', 'rest': ''},
    {'qty_before': '2', 'unit_before': 'шт', 'name': 'лука', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '500', 'unit_before': 'г', 'name': 'муки', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '200', 'unit_before': 'мл', 'name': 'молока', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': None, 'unit_before': 'шт', 'name': 'лука', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '1/2', 'unit_before': 'стакана', 'name': 'воды', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '3/4', 'unit_before': 'ч.л.', 'name': 'соли', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'морковь ', 'qty_after': '2', 'unit_after': 'шт', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'яйца ', 'qty_after': '3', 'unit_after': 'шт', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'сахар ', 'qty_after': '100', 'unit_after': 'г', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'мука', 'qty_after': '500', 'unit_after': 'г', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'молоко', 'qty_after': '200', 'unit_after': 'мл', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'соль', 'qty_after': None, 'unit_after': 'по вкусу', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'зелень', 'qty_after': None, 'unit_after': 'для украшения', 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'перец', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '2', 'unit_before': 'ст. л.', 'name': 'масла', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '1', 'unit_before': 'ч. л.', 'name': 'соды', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '500', 'unit_before': 'гр', 'name': 'фарша', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '2', 'unit_before': 'шт', 'name': 'яйца - свежие', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '500', 'unit_before': 'г', 'name': 'муки', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': '1', 'unit_before': 'ст.л.', 'name': 'масла', 'qty_after': None, 'unit_after': None, 'rest': ''},
    {'qty_before': None, 'unit_before': None, 'name': 'картошка', 'qty_after': '2', 'unit_after': 'шт', 'rest': '. = 240 г'},
    {'qty_before': None, 'unit_before': None, 'name': 'банан ', 'qty_after': '400', 'unit_after': 'г', 'rest': ' (2 шт.)'},
    {'qty_before': None, 'unit_before': None, 'name': 'мука ', 'qty_after': '20', 'unit_after': 'гр', 'rest': ' + 13гр на стол'},
    {'qty_before': None, 'unit_before': None, 'name': 'молоко', 'qty_after': None, 'unit_after': 'мл', 'rest': ''},
    {'qty_before': None, 'unit_before': 'шт', 'name': 'лука', 'qty_after': None, 'unit_after': None, 'rest': ''},
]
