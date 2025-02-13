import aiohttp
from .types import (
    CookidooConfig,
    CookidooShoppingRecipeDetails,
    Nutrition,
    RecipeIngredient,
    RecipeIngredientGroup,
    RecipeNutrition,
    RecipeStep,
    RecipeStepGroup,
    ServingSize,
    Time,
    TimeQuantity,
)
from .helpers import get_localization_options

async def get_country_options():
    locs = await get_localization_options()
    return list({loc.country_code for loc in locs})

async def get_language_options():
    locs = await get_localization_options()
    return list({loc.language for loc in locs})

class Cookidoo:
    def __init__(self, session: aiohttp.ClientSession, cfg: CookidooConfig = None):
        self._session = session
        if cfg is None:
            self._cfg = CookidooConfig()
        else:
            self._cfg = cfg

    @property
    def api_endpoint(self):
        return self._cfg.localization.url.rstrip("/")

    async def get_recipe_details(self, id: str) -> CookidooShoppingRecipeDetails:
        RECIPE_PATH = "recipes/recipe/{language}/{id}"
        url = f"{self.api_endpoint}/{RECIPE_PATH.format(language=self._cfg.localization.language, id=id)}"
        
        async with self._session.get(url, headers={"ACCEPT": "application/json"}, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")
            data = await response.json()
        
        # Fetch only Polish recipes
        if data.get("locale", "") != "pl":
            return None

        additionalInformation = [item.get("content", "") for item in data.get("additionalInformation", [])]

        categories = data.get("categories", [])
        category = categories[0].get("title", "") if categories else ""

        difficulty = data.get("difficulty", "")
        recipe_id = data.get("id", "")
        language = data.get("language", "")
        locale = data.get("locale", "")

        recipeNutritions = []
        for group in data.get("nutritionGroups", []):
            for rn in group.get("recipeNutritions", []):
                nutritions = []
                for n in rn.get("nutritions", []):
                    nutritions.append(Nutrition(
                        number=n.get("number", 0.0),
                        type=n.get("type", ""),
                        unittype=n.get("unittype", "")
                    ))
                recipeNutritions.append(RecipeNutrition(
                    nutritions=nutritions,
                    quantity=rn.get("quantity", 0),
                    unitNotation=rn.get("unitNotation", "")
                ))

        publicationDate = data.get("publicationDate", "")

        recipeIngredientGroups = []
        for group in data.get("recipeIngredientGroups", []):
            title = group.get("title", "")
            ingredients_list = []
            for ing in group.get("recipeIngredients", []):
                ingredients_list.append(RecipeIngredient(
                    ingredientNotation=ing.get("ingredientNotation", ""),
                    optional=ing.get("optional", False),
                    preparation=ing.get("preparation", ""),
                    quantity=ing.get("quantity", {}).get("value", 0),
                    unitNotation=ing.get("unitNotation", "")
                ))
            recipeIngredientGroups.append(RecipeIngredientGroup(
                title=title,
                recipeIngredients=ingredients_list
            ))

        recipeStepGroups = []
        for group in data.get("recipeStepGroups", []):
            title = group.get("title", "")
            steps_list = []
            for step in group.get("recipeSteps", []):
                steps_list.append(RecipeStep(
                    content=step.get("formattedText", "").strip(),
                    step=step.get("title", "").strip()
                ))
            recipeStepGroups.append(RecipeStepGroup(
                title=title,
                recipeSteps=steps_list
            ))

        recipeUtensils = [u.get("utensilNotation", "") for u in data.get("recipeUtensils", [])]

        serving = data.get("servingSize", {})
        servingSize = ServingSize(
            quantity=serving.get("quantity", {}).get("value", 0),
            unitNotation=serving.get("unitNotation", "")
        )

        targetCountries = data.get("targetCountries", [])
        thermomixVersions = data.get("thermomixVersions", [])

        times = []
        for t in data.get("times", []):
            tq = TimeQuantity(value=t.get("quantity", {}).get("value", 0))
            times.append(Time(
                comment=t.get("comment", ""),
                quantity=tq,
                type=t.get("type", "")
            ))

        title_final = data.get("title", "")

        details = CookidooShoppingRecipeDetails(
            additionalInformation=additionalInformation,
            category=category,
            difficulty=difficulty,
            id=recipe_id,
            language=language,
            locale=locale,
            recipeNutritions=recipeNutritions,
            publicationDate=publicationDate,
            recipeIngredientGroups=recipeIngredientGroups,
            recipeStepGroups=recipeStepGroups,
            recipeUtensils=recipeUtensils,
            servingSize=servingSize,
            targetCountries=targetCountries,
            thermomixVersions=thermomixVersions,
            times=times,
            title=title_final
        )
        return details
