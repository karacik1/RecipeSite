from _pyrepl import console
from itertools import product

from django.shortcuts import render, get_object_or_404
from unicodedata import category
from .forms import RecipeForm
from .models import Category, Recipe
from django.http import HttpResponse

from .services import got_recipe
from .services.got_recipe import got_form


# Create your views here.
def recipe_list(request, category_slug=None):
    categories = Category.objects.all()
    recipies = Recipe.objects.all()

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        recipies = recipies.filter(category=category)

    return render(request, 'RecipeSite/recipe/list.html',
                  {"category": category,
                   "categories": categories,
                   "recipies": recipies}, )


def recipe_detail(request, id, slug):
    recipe = get_object_or_404(Recipe, id=id, slug=slug)
    related_recipies = Recipe.objects.filter(category=recipe.category).exclude(id=recipe.id)[:4]
    return render(request, "RecipeSite/recipe/detail.html",
                  {'recipe':recipe,
                   'related_recipies': related_recipies})
def detail_recipe(request):
    recipe = get_object_or_404(Recipe, title="Чай")
    return render(request, 'RecipeSite/recipe/detail.html',
                  {
                      "description": recipe.description.split(" "),
                      "ingredients_list": recipe.ingredients.split(", "),
                      "recipe_name": recipe.title,
                      'url': recipe.original_URL,

                  })
def test(request):
    error=""
    if request.method == "POST":

        got_form(request.POST)
        print("Сервис отработал")
        # form_type = request.POST.get('form_type')
        #
        # if form_type == 'recipe':
        #     form = RecipeForm(request.POST)
        #     if form.is_valid():
        #         form.save()
        #
        #     else:
        #         error="плохая форма"
        # elif form_type == "url_recipe":
        #     recipe_url = request.POST.get("url")
        #     data = get_recipe_from_url(recipe_url)
        #
        #     return HttpResponse("Данные получены" + data)
        # else:
        #     print("ОШИБКА Полученняая странная форма не существует")

    form = RecipeForm()
    data={
        "form": form,
        "error": error,
    }
    return render(request,"RecipeSite/recipe/add_recipe.html", context=data)

