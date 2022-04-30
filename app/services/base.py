"""Services base"""
from typing import (AnyStr, Callable, Dict, Generator, Generic, Type, TypeVar,
                    Union, get_args)

from pydantic import BaseModel
from sqlalchemy.orm import Query, Session

from ..database import Base

MT = TypeVar("MT", bound=Base)
ST = TypeVar("ST", bound=BaseModel)


class NotFoundError(Exception):
    """Raised when a model with a given params are not found.

    Example:
        >>> raise NotFoundError(models.User, {"id": 1})
    """

    def __init__(self, model: Type[MT], params: dict):
        self.model = model
        self.id = params.get("id", None)
        self.params = params
        super().__init__(f"{model.__name__} not found with params: {params}")


class Service(Generic[MT, ST]):
    """Abstract Service class that provides CRUD operations for a SQLAlchemy model.
    Where typing MT is the SQLAlchemy model
    and ST is the Pydantic model(ST stands to Schema Type).

    Example:
    ```python
    class UserService(Service[User, UserBase]):
        ...
    ```

    :attr db: the database session
    :attr model: the SQLAlchemy model
    :attr query: the query for the model
    :attr __default_params__: the default parameters when creating model or filtering the query
    """

    __default_params__: Dict[str, Union[AnyStr, int, float, bool]] = {}

    def __init__(self, db: Session):
        """Initialize the service.
        :param db: the database session
        """
        self.db: Session = db
        types = get_args(self.__orig_bases__[0])  # pylint: disable=no-member
        self.model: Type[MT] = types[0]
        self.query = self.db.query(self.model)
        self._default_params = self.__default_params__.copy()

    def update_default_params(self, **kwargs: Dict[str, Union[AnyStr, int, float, bool]]) -> None:
        """Update the default parameters.
        :param kwargs: keyword arguments to update the default parameters with
        """
        self._default_params.update(kwargs)

    @property
    def default_params(self) -> Dict[str, Union[AnyStr, int, float, bool]]:
        """Get the default parameters."""
        return self._default_params.copy()

    def create_model(self, **kwargs) -> MT:
        """Create a new model instance.
        :param kwargs: keyword arguments to create the model with
        :return: the created model
        """
        return self.model(**kwargs, **self.default_params)

    def filter_by(self, **kwargs) -> Query:
        """Filter the query by the given keyword arguments.
        :param kwargs: keyword arguments to filter the query by
        :return: the filtered query
        """
        return self.query.filter_by(**kwargs, **self.default_params)

    def save(self, schema: ST) -> ST:
        """Save the given schema.
        :param schema: the schema to save
        :return: the saved schema
        """
        model = self.create_model(**schema.dict())
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_one(self, **kwargs) -> Union[ST, None]:
        """Get one model by the given keyword arguments.
        :return: the first model that matches the keyword arguments or None if no model matches
        """
        return self.filter_by(**kwargs).one()

    def get_one_or_raise(self, **kwargs) -> ST:
        """Get one model by the given keyword arguments.

        :param kwargs: keyword arguments to filter the query by
        :raises NotFoundError: if no model matches the keyword arguments
        :return: the first model that matches the keyword
                 arguments or raise a NotFoundError if no model matches
        """
        model = self.get_one(**kwargs)
        if model is None:
            raise NotFoundError(self.model, kwargs)
        return model

    def get_by_id(self, id_: int) -> ST:
        """Get a model by its id.
        :param id_: the id of the model to get
        :return: the model with the given id_
        """
        return self.get_one_or_raise(id=id_)

    def get_all(self) -> Generator[ST, None, None]:
        """Get all models.
        :return: a generator of all models
        """
        yield from self.find()

    def find(self, **kwargs) -> Generator[ST, None, None]:
        """Find models by the given keyword arguments.
        :param kwargs: keyword arguments to filter the query by
        :return: a generator of models that match the keyword arguments
        """
        yield from self.filter_by(**kwargs).all()

    def count(self, **kwargs) -> int:
        """Count the number of models that match the given keyword arguments.
        :param kwargs: keyword arguments to filter the query by
        :return: the number of models that match the keyword arguments
        """
        return self.filter_by(**kwargs).count()

    def delete(self, id_: int) -> None:
        """Delete a model by its id.
        :param id_: the id of the model to delete
        :param kwargs: keyword arguments to filter the query by
        """
        model = self.get_by_id(id_)
        self.db.delete(model)
        self.db.commit()

    def update(self, id_: int, model: ST) -> ST:
        """Update a model by its id.
        :param id_: the id of the model to update
        :param model: the model to update
        :return: the updated model
        """
        model = self.get_by_id(id_)
        for key, value in model.dict(exclude_unset=True).items():
            setattr(model, key, value)
        self.db.commit()
        self.db.refresh(model)
        return model


def get_service(service_class: Type[Service], db: Session, *args, **kwargs) -> Callable[[], Service]:
    """Wrap a service class in a function that returns a new instance of the service.

    :param service_class: the service class that will be wrapped
    :param args: the arguments to pass to the service class constructor
    :param kwargs: the keyword arguments to pass to the service class constructor
    :return: a function that returns a new instance of the service class
    """

    def inner() -> Service:
        return service_class(db=db, *args, **kwargs)

    return inner