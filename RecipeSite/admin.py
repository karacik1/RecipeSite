from django.contrib import admin
from django.db import transaction
from django.http import HttpResponseRedirect

from .models import Recipe, Category, ParseredSites, ingredients_set, ingredient_forms, Tag, SubTag, RecipeIngredient, \
    IngredientSuggestion, SuggestNewIngredientForms


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ParseredSites)
class ParsedSiteAdmin(admin.ModelAdmin):
    list_display = ("url", "parser_name")

@admin.register(ingredients_set)
class IngredientsSetAdmin(admin.ModelAdmin):
    list_display = ("name", )
    search_fields = ('name',)

@admin.register(ingredient_forms)
class IngredientFormsAdmin(admin.ModelAdmin):
    list_display = ("ingredient_form", "ingredient_correct_form")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "colour")
    ordering = ("name", )

@admin.register(SubTag)
class SubTagAdmin(admin.ModelAdmin):
    list_display = ("name", "tag")
    ordering = ("name", )

class RecipeIngredientInline(admin.TabularInline):
    """Встроенная форма для ингредиентов рецепта"""
    model = RecipeIngredient
    extra = 1  # ← Сколько пустых строк показывать
    autocomplete_fields = ['ingredient_id']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title',"get_ingredients", "created_at", "category", "get_tags")
    list_filter = ("created_at", "category")
    ordering = ("title", )

    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        # Оптимизация: загружаем теги одним запросом
        return super().get_queryset(request).prefetch_related('tags', 'ingredients')

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'

    def get_ingredients(self, obj):
        return ", ".join([ingredient.name for ingredient in obj.recipe_ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'


class SuggestNewIngredientFormsInline(admin.TabularInline):
    model = SuggestNewIngredientForms
    extra = 1
    fields = ('ingredient_form',)







@admin.register(IngredientSuggestion)
class IngredientSuggestionAdmin(admin.ModelAdmin):
    actions = ['approve_selected', "reject_selected"]
    list_display = ('normal_form', 'user', 'status', 'added_at', 'moderated_at')
    list_editable = ('status',)
    inlines = [SuggestNewIngredientFormsInline]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @admin.action(description="Одобрить выделенные ингридиенты")
    def  approve_selected(self, request, queryset):
        with transaction.atomic():
            for obj in queryset:
                if obj.status == 'accepted':
                    ingredient = ingredients_set.objects.create(name=obj.normal_form)
                    for form in obj.forms.all():
                        ingredient_forms.objects.create(ingredient_form = form.ingredient_form, ingredient_correct_form = ingredient)
                    obj.delete()

        self.message_user(request, "Готово!")

    @admin.action(description="Отклонить выделенные ингридиенты")
    def reject_selected(self, request, queryset):
        with transaction.atomic():
            for obj in queryset:
                if obj.status == 'rejected':
                    obj.delete()

        self.message_user(request, "Готово!")



    