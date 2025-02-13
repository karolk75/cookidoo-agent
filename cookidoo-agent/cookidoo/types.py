from dataclasses import dataclass, field
from typing import List

@dataclass
class CookidooLocalizationConfig:
    country_code: str = "ie"
    language: str = "en-GB"
    url: str = "https://gb.tmmobile.vorwerk-digital.com"

@dataclass
class CookidooConfig:
    localization: CookidooLocalizationConfig = field(default_factory=CookidooLocalizationConfig)
    email: str = ""
    password: str = ""

@dataclass
class Nutrition:
    number: float
    type: str
    unittype: str

@dataclass
class RecipeNutrition:
    nutritions: List[Nutrition]
    quantity: int
    unitNotation: str

@dataclass
class RecipeIngredient:
    ingredientNotation: str
    optional: bool
    preparation: str
    quantity: float
    unitNotation: str

@dataclass
class RecipeIngredientGroup:
    title: str
    recipeIngredients: List[RecipeIngredient]

@dataclass
class RecipeStep:
    content: str
    step: str

@dataclass
class RecipeStepGroup:
    title: str
    recipeSteps: List[RecipeStep]

@dataclass
class ServingSize:
    quantity: float
    unitNotation: str

@dataclass
class TimeQuantity:
    value: float

@dataclass
class Time:
    comment: str
    quantity: TimeQuantity
    type: str

@dataclass
class CookidooShoppingRecipeDetails:
    additionalInformation: List[str]
    category: str
    difficulty: str
    id: str
    language: str
    locale: str
    recipeNutritions: List[RecipeNutrition]
    publicationDate: str
    recipeIngredientGroups: List[RecipeIngredientGroup]
    recipeStepGroups: List[RecipeStepGroup]
    recipeUtensils: List[str]
    servingSize: ServingSize
    targetCountries: List[str]
    thermomixVersions: List[str]
    times: List[Time]
    title: str
