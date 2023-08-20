# Webtronics_task


## Test Task for Webtronics FastAPI candidate

### Description
Create a simple RESTful API using FastAPI for a social networking application

### Functional requirements
- There should be some form of authentication and registration (JWT, Oauth, Oauth 2.0, etc..)

- As a user I need to be able to signup and login
- As a user I need to be able to create, edit, delete and view posts
- As a user I can like or dislike other users’ posts but not my own
- The API needs a UI Documentation (Swagger/ReDoc)


### Bonus section
1) Use https://clearbit.com/platform/enrichment for getting additional data for the
user on signup
    - [-] not completed
2) Use emailhunter.co for verifying email existence on registration
    - [-] not completed
3) Use an in-memory DB for storing post likes and dislikes (As a cache, that gets
updated whenever new likes and dislikes get added)
    + [+] completed with redis


## Used technologies

### API:
1) Fastapi
2) fastapi_users - auth
3) Pydantic
### ORM and migration tools
1) SQLAlchemy
2) Alembic
### DB
1) PostgreSQL
2) asyncpg - driver
### Cache
1) Redis

## Api structure

### src/
Source api folder. Contains all apps.

#### cache_base.py
Configuration file for caching.

#### database.py
Configuration file for database.

#### main.py
Main script. collects all routers.

#### settings.py
Config file for whole project.

---
### App auth/
App for auth from fastapi_users.

#### base_config.py
Config file for fastapi_users.

In this project JWT strategy (JWT auth) used with cookie transportation (JWT stored in a cookie).

#### manager.py
User manager for User model from fastapi_users.
Adds some features for User model e.g. additional handling after registration/lofin.

#### models.py
`User` - table with mixin from fastapi_users.
Mixin adds service attributes for correct operation of fastapi_users (is_active flag, is_superuser etc.).

#### schemas.py
Pydantic schemas for fastapi_users.

#### utils.py
Some helper functions. Contains `get_user_db` for getting User object.

---
### App posts/

#### cache.py
Cache manipulation functions. `update_cache_reactions` for updating/adding row into redis.

#### dependencies.py
Dependencies for additional functional (validating of Post id, common params used in several functions).

#### exceptions.py
Posts exceptions. They are all based on HTTPExceptions.

#### models.py
Stores posts models.

`ReactionType` - PostgreSQL enumerate (at this moment contains only two reactions - **like** and **dislike**).

`Reaction` - Secondary table for m2m (User can like many posts, Post can have many users like it).
- `user_id`: combined pk "user_id-post_id", fk, UUID
- `post_id`: combined pk "user_id-post_id", fk, UUID
- `type`: ReactionType - PostgreSQL Enum 

`Post` - Post table.
- `id` - pk, UUID, default: uuid4
- `owner_id`: fk, UUID
- `owner`: SQLAlchemy relation
- `title`: str
- `description`: text
- `creation_date`: TIMESTAMP, default: Postgresql function **now()**
- `last_update_date`: TIMESTAMP, default: Postgresql function **now()**, updates when record is changed
- `user_reactions`: SQLAlchemy relation, set of User's objects.

#### router.py
Contains all routes of posts app.

More detailed see in Swagger (tag "posts").

#### schemas.py
Pydantic schemas for posts app.

Contains: 
1) `CreatePost` - used to receive user data to create new posts
2) `EditPost` - user to receive user data to update existing post; have validator for removing leading and trailing spaces

#### service.py
This file contains app specific business logic. Mostly it is retrieve data from db (or add) and process it.

---

### migrations/
Alembic folder for storing migrations and migration conf.

### alembic.ini
Alembic config file.

### Dockerfile.*
Dockerfiles for services.

### docker-compose.yml
Docker-compose file.

### init.sql 
Inital file for creating database in postgresql container.

## Installation

1) Clone project to the desired directory with this command:
    ```
    git clone https://github.com/Daniil7575/Webtronics_task.git
    ```
2) Go to the root folder of *project* (`Webtronics_task`)
3) Add `.env` file and fill it with data provided below (all fields were filled in in advance to save your time):
    ```
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=webtronics
    DB_USER=postgres
    DB_PASS=wejfhfYiug&687
    JWT_SECRET=d92fa843055391a9abe9b4d9011dee549383ab890cc15482d8e4869a9297ef1f
    REDIS_URL=cache
    REDIS_PORT=6379
    ```
4) Build and up containers with the following commands
    ```
    sudo docker compose build
    sudo docker compose up
    ```
5) Wait until everything starts. When it starts below text will be displayed in console:
    ```
    webtronics_task-api-1    | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    webtronics_task-api-1    | INFO  [alembic.runtime.migration] Will assume transactional DDL.
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Started server process [1]
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Started server process [1]
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Waiting for application startup.
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Waiting for application startup.
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Application startup complete.
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Application startup complete.
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    webtronics_task-api-1    | INFO:     [2023-08-20 16:27:08] Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    ```
6) Go to `http://0.0.0.0:8000/docs` or `http://127.0.01:8000/docs` and and you will be taken to Swagger.
