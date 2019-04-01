# HealthID-web-api

[![CircleCI](https://circleci.com/gh/bryanmezue/healthid-web-api/tree/dev.svg?style=svg&circle-token=fb99579bc192c2279835e181c7d81737f1d648a7)](https://circleci.com/gh/bryanmezue/healthid-web-api/tree/dev)

Health ID is an inventory management and customer engagement software platform designed for pharmacists/chemists and their customers. For pharmacists/chemists, Health ID helps them run their stores more efficiently and grow their business by improved targeting of promotions and value-added services. For consumers, Health ID improves their overall experience of pharmacies, provides personalised services and information, and also offers unique product discounts.

## Installing

```sh
    $ git clone https://github.com/bryanmezue/healthid-web-api.git
    $ cd healthid-web-api
    $ pip install virtualenv
    $ virtualenv venv
    $ source venv/bin/activate
    $ git checkout dev
    $ pip install -r requirements.txt
```

* Create a `.env` file and copy/paste the environment variables from the `.env_example` file that's already existent in the root project directory.
* Create a postgreSQL database called `healthid` using the default `postgres` user and change the value of variable `DB_PASSWORD` in your `.env` file to your `postgres` user's password.
* Run the following commands to make the database migrations.

```sh
    $ python manage.py makemigrations
    $ python manage.py migrate
```

## Running the application

Run the command below to run the application locally.
```sh
  $ python manage.py runserver
  ```


## Running the tests

Run the command below to run the tests for the application.
```sh
  $ python manage.py test
  ```

## Deployment

The application's deployment is still pending for the backend APIs. Details will be filled here as soon as it is ready.

## Built With

The project has been built with the following technologies so far:

* [Django](https://www.djangoproject.com/) - web framework for building websites using Python
* [GraphQL](https://graphql.org/) - query language for our APIs.
* [Virtual environment](https://virtualenv.pypa.io/en/stable/) - tool used to create isolated python environments
* [pip](https://pip.pypa.io/en/stable/) - package installer for Python
* [PostgreSQL](https://www.postgresql.org/) - database management system used to persists the application's data.