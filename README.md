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
├── README.md           # This file
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
class Service(Generic[MT]): # MT: model type
    ...

# so that the service class can be used as below
class UserService(Service[models.User]):
    ...
```

That way, now `UserService` can be used as a service for `models.User` model.


### Default params for `Service`

Some models may need represent a implicit relation. By example, a item is only allowed be fetch by its owner (That's could be a situation to attend a [scope][fastapi-oauth2-scopes]). So, it's possible to define a default param for `Service` class.

```python
# by fixing some `id` as default param
class ItemService(Service[models.Item]):
    __default_params__ = {'owner_id': 1}

# or injecting the value at runtime
class ItemService(Service[models.Item]):
    def __init__(self, owner_id: int):
        self.update_default_params({'owner_id': owner_id})
```

Note that when the `__init__` method is called, the `update_default_params` method must be called instead of set a new dict to `__default_params__`, otherwise the modification will not be applied.

To use the default params, the `default_params` attribute could be used.

```python
# by using the default params
class ItemService(Service[models.Item]):
    def get_item_on_my_way(self) -> models.Item:
        return self.query.filter_by(**self.default_params).first()
```

Once a default param is defined, every method envolving model creation or querying will inject the default param.
Even methods that update or delete the models will use the default param indirectly once them use `create_model` or `filter_by` methods.

## Some implementation goals

- [ ] Add test cases.
- [ ] Use a [config pattern][fastapi-config] to define the database connection and other settings.
- [ ] Implement a [scoped session][fastapi-oauth2-scopes] pattern.
- [ ] Implement some [background tasks][fastapi-background-tasks].
- [ ] Integrate with some queue system (like [Celery][fastapi-celery]).

[fastapi-background-tasks]: https://fastapi.tiangolo.com/advanced/background-tasks/
[fastapi-celery]: https://fastapi.tiangolo.com/tutorial/background-tasks/?h=celery#caveat
[fastapi-config]: https://fastapi.tiangolo.com/advanced/settings/#the-config-file
[fastapi-oauth2-scopes]: https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
[fastapi-tutorial]: https://fastapi.tiangolo.com/tutorial/
