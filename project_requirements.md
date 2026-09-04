# Recipe API — Project Requirements

## 1. Project Description

Recipe API is a purely back-end JSON API.

There is no front end.

The API will be demonstrated through FastAPI's interactive documentation at:

/docs

The system allows users to create, store, search, and retrieve recipes together
with their ingredients, quantities, measurements, instructions, and categories.

---

## 2. Core Features

The API must support:

- Creating recipes
- Storing recipes
- Retrieving recipes
- Updating recipes
- Deleting recipes
- Defining ingredients
- Defining ingredient amounts
- Defining ingredient units
- Supporting optional ingredient preparation
- Searching recipes by name
- Searching recipes by ingredient
- Searching recipes by category
- Combining search criteria
- Supporting ordered recipe instructions

---

## 3. Recipe

A recipe contains:

- id
- name
- description
- instructions
- category
- created_at

Later, after authentication is introduced, the Recipe will also contain:

- owner_id
- is_public

Later, for better search, the Recipe will contain:

- prep_minutes
- cook_minutes

---

## 4. Category

A category contains:

- id
- name

A recipe belongs to a category.

Examples:

- Breakfast
- Dinner
- Meal

---

## 5. Ingredient

An ingredient represents an ingredient that exists independently.

An ingredient contains:

- id
- name

The amount and unit do NOT belong directly to the Ingredient.

For example:

Flour can be used as:

- 2 cups in Pancakes
- 5 cups in Bread
- 3 cups in Cake

Therefore, the amount depends on the recipe.

---

## 6. RecipeIngredient

RecipeIngredient represents an ingredient being used by a particular recipe.

It contains:

- id
- recipe_id
- ingredient_id
- amount
- unit
- preparation

The following fields belong to RecipeIngredient:

- amount
- unit
- preparation

Preparation is optional.

Examples:

Flour:

- amount = 2
- unit = cups
- preparation = null

Bitter leaves:

- amount = 2
- unit = cups
- preparation = washed and chopped

---

## 7. Flexible Amounts

Amount may be a number or null.

Examples:

Normal amount:

{
    "name": "Palm oil",
    "amount": 1,
    "unit": "cup"
}

No specific numeric amount:

{
    "name": "Salt",
    "amount": null,
    "unit": "to taste"
}

Another example:

{
    "name": "Water",
    "amount": null,
    "unit": "as needed"
}

Therefore:

amount must support:

float | None

---

## 8. Recipe Instructions

A recipe must have an ordered set of instructions.

We will use the structured RecipeStep approach.

RecipeStep contains:

- id
- recipe_id
- step_number
- instruction

Example:

Step 1:
Wash the vegetables.

Step 2:
Cut the vegetables.

Step 3:
Heat the oil.

Step 4:
Cook the vegetables.

---

## 9. Users

Users are introduced at Stage 4.

A Recipe will then belong to a User.

The Recipe will gain:

- owner_id
- is_public

Before Stage 4, recipes are globally accessible.

From Stage 4 onward, authentication and authorization determine
what a user can see and change.

---

## 10. Authentication

Authentication will be implemented using:

- FastAPI
- OAuth2 Password Flow
- Password hashing
- JWT
- Bearer authentication

The project authentication configuration will use:

Access token:
15 minutes

Refresh token:
7 days

---

## 11. Database

The project will use:

PostgreSQL

SQLAlchemy:

SQLAlchemy 2.0

Database operations:

Fully asynchronous

SQLAlchemy model style:

Mapped
mapped_column

Timestamps:

func.now()

---

## 12. Core Database Tables

The project will contain:

- User
- Category
- Recipe
- Ingredient
- RecipeIngredient
- RecipeStep

---

## 13. Stage 1 — Basic CRUD

Endpoints:

POST /recipes

GET /recipes

GET /recipes/{id}

PUT /recipes/{id}

DELETE /recipes/{id}

---

## 14. Stage 2 — Ingredients

Endpoints:

POST /recipes/{recipe_id}/ingredients

GET /recipes/{recipe_id}/ingredients

PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

---

## 15. Stage 3 — Search

Examples:

GET /recipes?search=pasta

GET /recipes?ingredient=tomato

GET /recipes?category=dinner

GET /recipes?search=chicken&category=dinner

Search will also support:

- pagination
- sorting
- combined filters

---

## 16. Stage 4 — Authentication

Endpoints:

POST /auth/register

POST /auth/login

POST /auth/refresh

Authenticated recipe behavior:

GET /recipes

Public recipes:

GET /recipes/public

Recipes will have:

owner_id
is_public

---

## 17. Stage 5 — Better Search

Multiple ingredient search:

GET /recipes?ingredient=chicken&ingredient=rice

Time filtering:

GET /recipes?category=breakfast&max_time=30

Recipe will contain:

prep_minutes
cook_minutes

---

## 18. API Documentation

Every endpoint must be visible and callable through:

/docs

The application must run using:

uvicorn app.main:app --reload

---

## 19. Project Submission

The project must include:

- Public GitHub repository
- Clear commit history
- README.md
- .env.example
- DATABASE_URL configuration
- SECRET_KEY configuration from Stage 4
- Working API
- Working /docs documentation

Each completed stage should be committed separately.

The README should state the stage reached.