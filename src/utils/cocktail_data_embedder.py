import os
import json
import psycopg2

COCKTAILS_DIR = "data//cocktails//data//cocktails/"
INGREDIENTS_DIR = "data/cocktails/data/ingredients/"


def get_all_data_json_paths(root_dir):
    paths = []
    for subdir in os.listdir(root_dir):
        full_subdir = os.path.join(root_dir, subdir)
        if os.path.isdir(full_subdir):
            data_json = os.path.join(full_subdir, "data.json")
            if os.path.isfile(data_json):
                paths.append(data_json)
    return paths


def insert_cocktail(cur, cocktail):
    cur.execute(
        """
        INSERT INTO cocktails (
            id, name, instructions, created_at, updated_at, description, source, garnish, abv, glass, method, year
        ) VALUES (
            %(id)s, %(name)s, %(instructions)s, %(created_at)s, %(updated_at)s, %(description)s, %(source)s, %(garnish)s, %(abv)s, %(glass)s, %(method)s, %(year)s
        ) ON CONFLICT DO NOTHING;
    """,
        {
            "id": cocktail.get("_id"),
            "name": cocktail.get("name"),
            "instructions": cocktail.get("instructions"),
            "created_at": cocktail.get("created_at"),
            "updated_at": cocktail.get("updated_at"),
            "description": cocktail.get("description"),
            "source": cocktail.get("source"),
            "garnish": cocktail.get("garnish"),
            "abv": cocktail.get("abv"),
            "glass": cocktail.get("glass"),
            "method": cocktail.get("method"),
            "year": cocktail.get("year"),
        },
    )


def insert_ingredient(cur, ingredient):
    pass
    # cur.execute(
    #     ap
    #     """
    #     INSERT INTO ingredients (
    #         id, _parent_id, name, strength, description, origin, color, category, created_at, updated_at, images, ingredient_parts, prices, calculator_id, sugar_g_per_ml, acidity, distillery, units
    #     ) VALUES (
    #         %(id)s, %(parent_id)s, %(name)s, %(strength)s, %(description)s, %(origin)s, %(color)s, %(category)s, %(created_at)s, %(updated_at)s, %(images)s, %(ingredient_parts)s, %(prices)s, %(calculator_id)s, %(sugar_g_per_ml)s, %(acidity)s, %(distillery)s, %(units)s
    #     ) ON CONFLICT DO NOTHING;
    # """,
    #     {
    #         "id": ingredient.get("_id"),
    #         "parent_id": ingredient.get("_parent_id"),
    #         "name": ingredient.get("name"),
    #         "strength": ingredient.get("strength"),
    #         "description": ingredient.get("description"),
    #         "origin": ingredient.get("origin"),
    #         "color": ingredient.get("color"),
    #         "category": ingredient.get("category"),
    #         "created_at": ingredient.get("created_at"),
    #         "updated_at": ingredient.get("updated_at"),
    #         "images": json.dumps(ingredient.get("images")),
    #         "ingredient_parts": json.dumps(ingredient.get("ingredient_parts")),
    #         "prices": json.dumps(ingredient.get("prices")),
    #         "calculator_id": ingredient.get("calculator_id"),
    #         "sugar_g_per_ml": ingredient.get("sugar_g_per_ml"),
    #         "acidity": ingredient.get("acidity"),
    #         "distillery": ingredient.get("distillery"),
    #         "units": ingredient.get("units"),
    #     },
    # )


def main():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="ved123"
    )
    cur = conn.cursor()

    for path in get_all_data_json_paths(COCKTAILS_DIR):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cocktail = json.load(f)
                insert_cocktail(cur, cocktail)
        except (json.JSONDecodeError, FileNotFoundError, IOError, UnicodeDecodeError) as e:
            print(f"Error loading cocktail file {path}: {e}")
            continue

    # for path in get_all_data_json_paths(INGREDIENTS_DIR):
    #     try:
    #         with open(path, 'r', encoding='utf-8') as f:
    #             ingredient = json.load(f)
    #             insert_ingredient(cur, ingredient)
    #     except (json.JSONDecodeError, FileNotFoundError, IOError, UnicodeDecodeError) as e:
    #         print(f"Error loading ingredient file {path}: {e}")
    #         continue

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
