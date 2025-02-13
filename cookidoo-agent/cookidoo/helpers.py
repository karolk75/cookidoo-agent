from .types import CookidooLocalizationConfig

async def get_localization_options(country: str = None, language: str = None):
    loc = CookidooLocalizationConfig()
    if country:
        loc.country_code = country
    if language:
        loc.language = language
    return [loc]
