# FastAPI Tutorial

Project aimed to follow and learn from [FastAPI Tutorial][fastapi-tutorial].

## Directory structure

```
.
├── app/                # Application module by itself
│  ├── auth.py          # Authentication module
│  ├── database.py      # Database definition
│  ├── main.py          # App definition
│  ├── models.py        # Models declaration
│  ├── routers/         # Sub-routers definition
│  ├── schemas/         # Schemas definition
│  └── services/        # Service pattern implementation
├── README.md
└── requirements.txt    # Library dependencies
```

## Usage

```
$ pip install -r requirements.txt
$ uvicorn app.main:app --reload
```

## About the `services/` module

The core point of this module is to provide a service pattern implementation.
There is a abstract class named `Service` that is the base class for all services.

Basically, `Service` class implements CRUD operations for a model, aside some convenience methods.

### How to inherit from `Service`

The derived class must define the target model via typing.

```python
# once service class is defined as below
class Service(Generic[MT, ST]):
    ...

# so that the service class can be used as below
class UserService(Service[models.User, schemas.User]):
    ...
```

That way, now `UserService` can be used as a service for `models.User` model.


### Default params for `Service`

Some models may need represent a implicit relation. By example, a item is only allowed be fetch by its owner (That's could be a situation to attend a scope). So, it's possible to define a default param for `Service` class.

```python
# by fixing some `id` as default param
class ItemService(Service[models.Item, schemas.Item]):
    __default_params__ = {'owner_id': 1}

# or injecting the value at runtime
class ItemService(Service[models.Item, schemas.Item]):
    def __init__(self, owner_id: int):
        self._default_params['owner_id'] = owner_id
```

> Note that when the `__init__` method is called, the attribute `_default_params` must be updated.

Once a default param is defined, every method envolving model creation or querying will inject the default param. Even methods that update or delete the models will use the default param indirectly.


[fastapi-tutorial]: https://fastapi.tiangolo.com/tutorial/