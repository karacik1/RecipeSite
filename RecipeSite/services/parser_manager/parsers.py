# from urllib.robotparser import normalize

from RecipeSite.services.parser_manager.parser_base import RecipeGet


# from RecipeSite import tests
# from RecipeSite.models import ingredients_set, ingredient_forms

class russianfood_com(RecipeGet):
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
        for position, row in enumerate(table, 1):
            parsed_ingredient = RecipeGet.ingredient_normalize(" ".join(row.stripped_strings), position)
            ingredients.append(parsed_ingredient)
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



Parsers_list = {
    "russianfood.com": russianfood_com,
    "food_ru": food_ru
}

