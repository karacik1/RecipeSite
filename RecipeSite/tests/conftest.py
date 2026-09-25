import pytest


@pytest.fixture
def recipe_get():
    from RecipeSite.services.parser_manager.parser_base import RecipeGet
    return RecipeGet


@pytest.fixture(params=[
        ['лука 2 шт',
         {'name': 'лука',
          'amount': '2',
          'unit': 'шт',
          'extra': '',
          'raw_text': 'лука 2 шт',
          'position': 1}],
        ['мука 10гр',
         {'name': 'мука',
          'amount': '10',
          'unit': 'гр',
          'extra': '',
          'raw_text': 'мука 10гр',
          'position': 1}],
    ])
def simple_name_unit_amount(request):
    return request.param


@pytest.fixture(params=[
        ['2 шт лука',
         {'name': 'лука',
          'amount': '2',
          'unit': 'шт',
          'extra': '',
          'raw_text': '2 шт лука',
          'position': 1}],
        ['500 г муки',
         {'name': 'муки',
          'amount': '500',
          'unit': 'г',
          'extra': '',
          'raw_text': '500 г муки',
          'position': 1}],
        ['200 мл молока',
         {'name': 'молока',
          'amount': '200',
          'unit': 'мл',
          'extra': '',
          'raw_text': '200 мл молока',
          'position': 1}],
    ])
def ingredient_unit_amount_name(request):
    return request.param


@pytest.fixture(params=[
        [' шт лука',
         {'name': 'лука',
          'amount': "",
          'unit': 'шт',
          'extra': '',
          'raw_text': 'шт лука',
          'position': 1}],
        ['мл молоко',
         {'name': 'молоко',
          'amount': "",
          'unit': 'мл',
          'extra': '',
          'raw_text': 'мл молоко',
          'position': 1}]])
def without_amount(request):
    return request.param


@pytest.fixture(params=[['1/2 стакана воды',
             {'name': 'воды',
              'amount': '1/2',
              'unit': 'стакана',
              'extra': '',
              'raw_text': '1/2 стакана воды',
              'position': 1}],
            ['3/4 ч.л. соли',
             {'name': 'соли',
              'amount': '3/4',
              'unit': 'ч.л.',
              'extra': '',
              'raw_text': '3/4 ч.л. соли',
              'position': 1}]])
def amount_is_fractions(request):
    return request.param

@pytest.fixture(params=[
            ['мука: 500 г',
             {'name': 'мука',
              'amount': '500',
              'unit': 'г',
              'extra': '',
              'raw_text': 'мука: 500 г',
              'position': 1}],
            ['яйца — 3 шт',
             {'name': 'яйца',
              'amount': '3',
              'unit': 'шт',
              'extra': '',
              'raw_text': 'яйца — 3 шт',
              'position': 1}],
        ])
def with_special_sep(request):
    return request.param


@pytest.fixture(params=[
            ['соль по вкусу',
             {'name': 'соль',
              'amount': "",
              'unit': 'по вкусу',
              'extra': '',
              'raw_text': 'соль по вкусу',
              'position': 1}],
            ['зелень для украшения',
             {'name': 'зелень',
              'amount': "",
              'unit': 'для украшения',
              'extra': '',
              'raw_text': 'зелень для украшения',
              'position': 1}],
        ])
def special_unit(request):
    return request.param


@pytest.fixture(params=[
            ['2 ст. л. масла',
             {'name': 'масла',
              'amount': '2',
              'unit': 'ст. л.',
              'extra': '',
              'raw_text': '2 ст. л. масла',
              'position': 1}],
            ['1 ч. л. соды',
             {'name': 'соды',
              'amount': '1',
              'unit': 'ч. л.',
              'extra': '',
              'raw_text': '1 ч. л. соды',
              'position': 1}],
            ['1ст л масла',
             {'name': 'масла',
              'amount': '1',
              'unit': 'ст л',
              'extra': '',
              'raw_text': '1ст л масла',
              'position': 1}],
        ])
def duble_unit_nam(request):
    return request.param


@pytest.fixture
def only_name():
    return ['перец',
             {'name': 'перец',
              'amount': "",
              'unit': "",
              'extra': '',
              'raw_text': 'перец',
              'position': 1}]



@pytest.fixture(params=[
            ['2 шт. картошка  = 240 г',
             {'name': 'картошка',
              'amount': '2',
              'unit': 'шт.',
              'extra': '  = 240 г',
              'raw_text': '2 шт. картошка  = 240 г',
              'position': 1}],
            ['банан - 400 г (2 шт.)',
             {'name': 'банан',
              'amount': '400',
              'unit': 'г',
              'extra': ' (2 шт.)',
              'raw_text': 'банан - 400 г (2 шт.)',
              'position': 1}],
            ['мука : 20гр + 13гр на стол',
             {'name': 'мука',
              'amount': '20',
              'unit': 'гр',
              'extra': ' + 13гр на стол',
              'raw_text': 'мука : 20гр + 13гр на стол',
              'position': 1}],
        ])
def unit_amount_unit_rest(request):
    return request.param
