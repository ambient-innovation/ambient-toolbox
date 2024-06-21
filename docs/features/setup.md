# Setup

## Default installation

Setting up and getting started with this toolbox is very simple. At first make sure you are installing the latest
version of `ambient-toolbox`:

* Installation via pip:

  `pip install -U ambient-toolbox`

* Installation via pipenv:

  `pipenv install ambient-toolbox`

Afterwards, include the package in your ``INSTALLED_APPS`` within your main
[django settings file](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-INSTALLED_APPS):

````python
INSTALLED_APPS = (
    ...
    'ambient_toolbox',
)
 ````

## Installing the djangorestframework extension

If you wish to use the extensions for [djangorestframework](https://www.django-rest-framework.org/), simply install the
toolbox with the desired extension:

* Installation via pip:

  `pip install -U ambient-toolbox[drf]`

* Installation via pipenv:

  `pipenv install ambient-toolbox[drf]`

## Installing the GraphQL extension

If you wish to use the extensions for [django-graphene](https://pypi.org/project/graphene-django/), simply install the
toolbox with the desired extension:

* Installation via pip:

  `pip install -U ambient-toolbox[graphql]`

* Installation via pipenv:

  `pipenv install ambient-toolbox[graphql]`

# Installing multiple extensions

In the case that you want to install more than one extension, just chain the extension with a comma:

* Installation via pip:

  `pip install -U ambient-toolbox[drf,graphql]`

* Installation via pipenv:

  `pipenv install ambient-toolbox[drf,graphql]`
