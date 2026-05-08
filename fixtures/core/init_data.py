from core.models import State, City, Country
import json


# ----------------
arquivo_json = "fixtures/core/data/country.json"
with open(arquivo_json, 'r', encoding='utf-8') as file:
    country_data = json.load(file)

for item in country_data:
    Country.objects.get_or_create(
        country_code=item.get("country_code"),
        defaults={
            "name": item.get("name"),
        }
    )

# ----------------
arquivo_json = "fixtures/core/data/state.json"
with open(arquivo_json, 'r', encoding='utf-8') as file:
    state_data = json.load(file)

for item in state_data:
    obj_country = Country.objects.get(
        name=item.get("country_name"),
        country_code=item.get("country_code")
    )

    State.objects.get_or_create(
        cod=item.get("cod"),
        defaults={
            "name": item.get("name"),
            "country": obj_country,
            "uf": item.get("uf"),
        }
    )

# ----------------
arquivo_json = "fixtures/core/data/city.json"
with open(arquivo_json, 'r', encoding='utf-8') as file:
    city_data = json.load(file)

for item in city_data:
    state_obj = State.objects.get(
        cod=item.get("state_cod")
    )

    City.objects.get_or_create(
        cod=item.get("cod"),
        defaults={
            "name": item.get("name"),
            "state": state_obj,
        }
    )