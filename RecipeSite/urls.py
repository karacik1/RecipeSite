
from django.urls import path
from . import views

app_name = "RecipeSite"
urlpatterns = [
    path("test/", views.test, name="test")    ,
    path("", views.recipe_list, name="recipe_list"),
    path('slug:category_slug>/', views.recipe_list, name="recipe_list_by_category"),
    path("<int:id>/<slug:slug>", views.recipe_detail, name="product_detail"),

]