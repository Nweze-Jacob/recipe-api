# Recipe API — API Design

## 1. API Purpose

The Recipe API is a purely back-end JSON API.

There is no front end.

The API will be tested and demonstrated through FastAPI's interactive
documentation at:

/docs

The API allows users to create, store, search, and retrieve recipes together
with their ingredients, quantities, measurements, instructions, and categories.

---

# 2. HTTP Methods

The API will use standard HTTP methods.

## GET

Used to retrieve resources.

Examples:

GET /recipes

GET /recipes/{id}

---

## POST

Used to create resources.

Examples:

POST /recipes

POST /auth/register

---

## PUT

Used to update an existing resource.

Examples:

PUT /recipes/{id}

PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

---

## DELETE

Used to delete an existing resource.

Examples:

DELETE /recipes/{id}

DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

---

# 3. API Endpoint Groups

The API will contain these major endpoint groups:

1. Recipe endpoints
2. Recipe ingredient endpoints
3. Recipe step endpoints
4. Authentication endpoints
5. Recipe search endpoints

---

# 4. STAGE 1 — BASIC CRUD

Stage 1 implements basic recipe CRUD.

Required endpoints:

POST /recipes

GET /recipes

GET /recipes/{id}

PUT /recipes/{id}

DELETE /recipes/{id}

---

# 5. POST /recipes

## Purpose

Create a new recipe.

## Method

POST

## URL

/recipes

## Request Body

Example:

{
    "name": "Pancakes",
    "description": "Simple homemade pancakes",
    "category_id": 1
}

## Response

Example:

{
    "id": 12,
    "name": "Pancakes",
    "description": "Simple homemade pancakes",
    "category": "Breakfast",
    "ingredients": [],
    "instructions": []
}

## Success Status

201 Created

## Possible Errors

400 Bad Request

404 Not Found

422 Unprocessable Entity

---

# 6. GET /recipes

## Purpose

Retrieve recipes.

## Method

GET

## URL

/recipes

## Stage 1 Behavior

At Stage 1, this endpoint retrieves recipes.

At Stage 4, the endpoint will represent the authenticated user's recipes.

## Response

Example:

[
    {
        "id": 12,
        "name": "Pancakes",
        "description": "Simple homemade pancakes",
        "category": "Breakfast",
        "ingredients": [],
        "instructions": []
    }
]

## Success Status

200 OK

---

# 7. GET /recipes/{id}

## Purpose

Retrieve one recipe by ID.

## Method

GET

## URL

/recipes/{id}

Example:

GET /recipes/12

## Response

Example:

{
    "id": 12,
    "name": "Pancakes",
    "category": "Breakfast",
    "ingredients": [
        {
            "name": "Flour",
            "amount": 2,
            "unit": "cups"
        },
        {
            "name": "Milk",
            "amount": 1.5,
            "unit": "cups"
        },
        {
            "name": "Eggs",
            "amount": 2,
            "unit": "pieces"
        }
    ],
    "instructions": [
        "Add the flour to a mixing bowl.",
        "Add the milk and eggs.",
        "Mix until the batter is smooth.",
        "Heat a pan over medium heat.",
        "Pour the batter into the pan and cook until golden brown on both sides."
    ]
}

## Success Status

200 OK

## Not Found

404 Not Found

---

# 8. PUT /recipes/{id}

## Purpose

Update an existing recipe.

## Method

PUT

## URL

/recipes/{id}

Example:

PUT /recipes/12

## Request Body

Example:

{
    "name": "Fluffy Pancakes",
    "description": "Updated pancake recipe",
    "category_id": 1
}

## Success Status

200 OK

## Possible Errors

404 Not Found

422 Unprocessable Entity

At Stage 4:

403 Forbidden may be returned when the authenticated user does not own
the recipe.

---

# 9. DELETE /recipes/{id}

## Purpose

Delete a recipe.

## Method

DELETE

## URL

/recipes/{id}

Example:

DELETE /recipes/12

## Success Status

204 No Content

## Possible Errors

404 Not Found

At Stage 4:

403 Forbidden if the authenticated user does not own the recipe.

---

# 10. STAGE 2 — RECIPE INGREDIENTS

Stage 2 adds relationship operations.

Required endpoints:

POST /recipes/{recipe_id}/ingredients

GET /recipes/{recipe_id}/ingredients

PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

The important ID is:

recipe_ingredient_id

not:

ingredient_id

The recipe ingredient ID identifies the relationship record.

---

# 11. POST /recipes/{recipe_id}/ingredients

## Purpose

Add an ingredient to a recipe.

## Method

POST

## URL

/recipes/{recipe_id}/ingredients

Example:

POST /recipes/12/ingredients

## Request Body

Example:

{
    "name": "Flour",
    "amount": 2,
    "unit": "cups",
    "preparation": null
}

## Another Valid Request

{
    "name": "Salt",
    "amount": null,
    "unit": "to taste"
}

## Response

Example:

{
    "id": 25,
    "ingredient": {
        "id": 1,
        "name": "Flour"
    },
    "amount": 2,
    "unit": "cups",
    "preparation": null
}

## Success Status

201 Created

---

# 12. GET /recipes/{recipe_id}/ingredients

## Purpose

Retrieve all ingredients belonging to a recipe.

## Method

GET

## URL

/recipes/{recipe_id}/ingredients

Example:

GET /recipes/12/ingredients

## Response

Example:

[
    {
        "id": 25,
        "name": "Flour",
        "amount": 2,
        "unit": "cups",
        "preparation": null
    },
    {
        "id": 26,
        "name": "Milk",
        "amount": 1.5,
        "unit": "cups",
        "preparation": null
    }
]

## Success Status

200 OK

---

# 13. PUT /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

## Purpose

Update an ingredient's information for a particular recipe.

## Method

PUT

## URL

/recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

Example:

PUT /recipes/12/ingredients/25

## Request Body

Example:

{
    "amount": 3,
    "unit": "cups",
    "preparation": null
}

## Success Status

200 OK

---

# 14. DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

## Purpose

Remove an ingredient from a recipe.

## Method

DELETE

## URL

/recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

Example:

DELETE /recipes/12/ingredients/25

## Success Status

204 No Content

---

# 15. RECIPE STEPS

This project uses a RecipeStep table to store ordered instructions.

These endpoints support our chosen implementation.

POST /recipes/{recipe_id}/steps

GET /recipes/{recipe_id}/steps

PUT /recipes/{recipe_id}/steps/{step_id}

DELETE /recipes/{recipe_id}/steps/{step_id}

These are implementation endpoints for the RecipeStep approach. They are
not additional mandatory endpoints in the facilitator's staged endpoint list.

---

# 16. POST /recipes/{recipe_id}/steps

## Purpose

Add an instruction step.

## Method

POST

## URL

/recipes/{recipe_id}/steps

## Request Body

{
    "step_number": 1,
    "instruction": "Add the flour to a mixing bowl."
}

## Success Status

201 Created

---

# 17. GET /recipes/{recipe_id}/steps

## Purpose

Retrieve the ordered steps of a recipe.

## Method

GET

## URL

/recipes/{recipe_id}/steps

## Response

[
    {
        "id": 1,
        "step_number": 1,
        "instruction": "Add the flour to a mixing bowl."
    },
    {
        "id": 2,
        "step_number": 2,
        "instruction": "Add the milk and eggs."
    }
]

## Success Status

200 OK

---

# 18. PUT /recipes/{recipe_id}/steps/{step_id}

## Purpose

Update an individual recipe step.

## Method

PUT

## URL

/recipes/{recipe_id}/steps/{step_id}

## Request Body

{
    "step_number": 1,
    "instruction": "Add the flour and sugar to a mixing bowl."
}

## Success Status

200 OK

---

# 19. DELETE /recipes/{recipe_id}/steps/{step_id}

## Purpose

Delete an individual recipe step.

## Method

DELETE

## URL

/recipes/{recipe_id}/steps/{step_id}

## Success Status

204 No Content

---

# 20. STAGE 3 — SEARCH

Stage 3 adds recipe searching.

Supported searches:

GET /recipes?search=pasta

GET /recipes?ingredient=tomato

GET /recipes?category=dinner

GET /recipes?search=chicken&category=dinner

---

# 21. Search by Recipe Name

## Request

GET /recipes?search=pasta

## Meaning

Return recipes whose name matches the search value.

---

# 22. Search by Ingredient

## Request

GET /recipes?ingredient=tomato

## Meaning

Return recipes containing the specified ingredient.

The query will use the relationship:

Recipe
    ↓
RecipeIngredient
    ↓
Ingredient

---

# 23. Search by Category

## Request

GET /recipes?category=dinner

## Meaning

Return recipes belonging to the specified category.

---

# 24. Combined Search

## Request

GET /recipes?search=chicken&category=dinner

## Meaning

Return recipes matching both criteria.

---

# 25. Pagination

Recipe listing will support pagination.

Example:

GET /recipes?page=1&limit=10

Where:

page = page number

limit = number of records per page

---

# 26. Sorting

Recipe listing will support sorting.

Example:

GET /recipes?sort=created_at

The exact implementation of sorting will be handled later.

---

# 27. STAGE 4 — AUTHENTICATION

Stage 4 introduces users and ownership.

Required authentication endpoints:

POST /auth/register

POST /auth/login

POST /auth/refresh

---

# 28. POST /auth/register

## Purpose

Register a new user.

## Method

POST

## URL

/auth/register

## Request Body

Example:

{
    "email": "user@example.com",
    "password": "StrongPassword123"
}

The password will be hashed before being stored.

Plaintext passwords will never be stored in the database.

## Success Status

201 Created

---

# 29. POST /auth/login

## Purpose

Authenticate a user.

## Method

POST

## URL

/auth/login

## Authentication Mechanism

OAuth2 Password Flow

Bearer authentication

JWT

## Request

The endpoint will use FastAPI's OAuth2 password form.

## Response

Example:

{
    "access_token": "JWT_ACCESS_TOKEN",
    "refresh_token": "JWT_REFRESH_TOKEN",
    "token_type": "bearer"
}

## Token Expiration

Access token:

15 minutes

Refresh token:

7 days

---

# 30. POST /auth/refresh

## Purpose

Generate a new access token using a valid refresh token.

## Method

POST

## URL

/auth/refresh

## Request

The refresh token will be supplied according to the authentication design.

## Response

Example:

{
    "access_token": "NEW_JWT_ACCESS_TOKEN",
    "refresh_token": "NEW_OR_EXISTING_REFRESH_TOKEN",
    "token_type": "bearer"
}

Access token expiration:

15 minutes

Refresh token expiration:

7 days

---

# 31. Bearer Authentication

Protected endpoints will use:

Authorization: Bearer <access_token>

The access token will be a JWT.

---

# 32. Authentication vs Authorization

Authentication answers:

"Who are you?"

Authorization answers:

"Are you allowed to perform this operation?"

For example:

User A owns Recipe 12.

User B attempts:

PUT /recipes/12

The API must prevent User B from modifying User A's recipe.

---

# 33. User-Owned Recipes

At Stage 4, Recipe gains:

owner_id

is_public

The relationship becomes:

User
 |
 | 1
 |
 | *
 v
Recipe

---

# 34. GET /recipes at Stage 4

At Stage 4:

GET /recipes

means:

Return recipes belonging to the authenticated user.

The authenticated user's identity will come from the JWT.

---

# 35. GET /recipes/public

## Purpose

Retrieve recipes that users have chosen to make public.

## Method

GET

## URL

/recipes/public

## Success Status

200 OK

---

# 36. STAGE 5 — BETTER SEARCH

Stage 5 adds more advanced search.

---

# 37. Multiple Ingredient Search

Example:

GET /recipes?ingredient=chicken&ingredient=rice

## Meaning

Return recipes containing BOTH:

- chicken
- rice

The API must not simply return recipes containing either ingredient.

---

# 38. Maximum Time Search

Example:

GET /recipes?category=breakfast&max_time=30

The recipe will contain:

prep_minutes

cook_minutes

The max_time filter will be used to find recipes within the requested time.

---

# 39. Final Endpoint Summary

## Stage 1

POST   /recipes

GET    /recipes

GET    /recipes/{id}

PUT    /recipes/{id}

DELETE /recipes/{id}


## Stage 2

POST   /recipes/{recipe_id}/ingredients

GET    /recipes/{recipe_id}/ingredients

PUT    /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}

DELETE /recipes/{recipe_id}/ingredients/{recipe_ingredient_id}


## RecipeStep

POST   /recipes/{recipe_id}/steps

GET    /recipes/{recipe_id}/steps

PUT    /recipes/{recipe_id}/steps/{step_id}

DELETE /recipes/{recipe_id}/steps/{step_id}


## Stage 4

POST /auth/register

POST /auth/login

POST /auth/refresh

GET /recipes/public


## Stage 3 and Stage 5 Search

GET /recipes?search=pasta

GET /recipes?ingredient=tomato

GET /recipes?category=dinner

GET /recipes?search=chicken&category=dinner

GET /recipes?ingredient=chicken&ingredient=rice

GET /recipes?category=breakfast&max_time=30

GET /recipes?page=1&limit=10

---

# 40. Standard Status Codes

201 Created

Used when a new resource is created.

200 OK

Used for successful retrieval and updates.

204 No Content

Used for successful deletion.

400 Bad Request

Used when the request is invalid.

401 Unauthorized

Used when authentication is missing or invalid.

403 Forbidden

Used when the authenticated user is not allowed to perform the operation.

404 Not Found

Used when a requested resource does not exist.

409 Conflict

Used when a request conflicts with existing data.

422 Unprocessable Entity

Used for request validation errors.

500 Internal Server Error

Used for unexpected server errors.

---

# 41. API Architecture

The eventual request flow will be:

Client
   ↓
FastAPI Router
   ↓
Authentication
   ↓
Authorization
   ↓
Pydantic Validation
   ↓
Business Logic / Service
   ↓
Repository
   ↓
Async SQLAlchemy 2.0
   ↓
PostgreSQL
   ↓
Response
   ↓
Client

---

# 42. Authentication Flow

Login:

Client
   ↓
POST /auth/login
   ↓
OAuth2PasswordRequestForm
   ↓
Find User
   ↓
Verify Password
   ↓
Create JWT Access Token
   ↓
Create JWT Refresh Token
   ↓
Return Bearer Tokens

Accessing protected resource:

Client
   ↓
Authorization: Bearer <JWT>
   ↓
FastAPI OAuth2 dependency
   ↓
Decode JWT
   ↓
Identify User
   ↓
Authorization Check
   ↓
Business Logic
   ↓
Database
   ↓
Response