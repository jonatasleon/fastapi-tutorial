"""Services base"""
from typing import AnyStr, Dict, Generator, Generic, Type, TypeVar, Union

from sqlalchemy.orm import Query, Session

from ..database import Base

MT = TypeVar("MT", bound=Base)


class NotFoundError(Exception):
    """Raised when a model with a given params are not found.

    Example:
        >>> raise NotFoundError(models.User, {"id": 1})

    :param model: The model class
    :param params: The params used to find the model
    """

    def __init__(self, model: Type[MT], params: dict):
        self.model = model
        self.id = params.get("id", None)
        self.params = params
        super().__init__(f"{model.__name__} not found with params: {params}")


class Service(Generic[MT]):
    """Abstract Service class that provides CRUD operations for a SQLAlchemy model.
    Where typing MT is the SQLAlchemy model

    Example:
    ```python
    class UserService(Service[User, UserBase]):
        ...
    ```

    :param db: the database session
    :param default_params: the default parameters to use when creating a model
    """

    __default_params__: Dict[str, Union[AnyStr, int, float, bool]] = {}
    __model__: Type[MT] = None

    def __init__(
        self, db: Session, *, default_params: Dict[str, Union[AnyStr, int, float, bool]] = None
    ):
        self.db: Session = db
        if not self.__model__:
            raise NotImplementedError("__model__ attribute must be defined")
        self.model: Type[MT] = self.__model__
        self.query = self.db.query(self.model)
        self._default_params = (self.__default_params__ or {}).copy()
        self.update_default_params(**(default_params or {}))

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
        return self.model(**{**self.default_params, **kwargs})

    def filter_by(self, **kwargs) -> Query:
        """Filter the query by the given keyword arguments.
        :param kwargs: keyword arguments to filter the query by
        :return: the filtered query
        """
        return self.query.filter_by(**{**self.default_params, **kwargs})

    def save(self, model: MT) -> MT:
        """Save the given model.
        :param model: the model to save
        :return: the saved model
        """
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_one(self, **kwargs) -> Union[MT, None]:
        """Get one model by the given keyword arguments.
        :return: the first model that matches the keyword arguments or None if no model matches
        """
        return self.filter_by(**kwargs).one_or_none()

    def get_one_or_raise(self, **kwargs) -> MT:
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

    def get_by_id(self, id_: int) -> MT:
        """Get a model by its id.
        :param id_: the id of the model to get
        :return: the model with the given id_
        """
        return self.get_one_or_raise(id=id_)

    def get_all(self) -> Generator[MT, None, None]:
        """Get all models.
        :return: a generator of all models
        """
        yield from self.find()

    def find(self, **kwargs) -> Generator[MT, None, None]:
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

    def update(self, model: MT) -> MT:
        """Update a model by its id.
        :param id_: the id of the model to update
        :param model: the model to update
        :return: the updated model
        """
        model = self.get_by_id(model.id)
        for key, value in model.__dict__.items():
            if key in model.__table__.columns.keys():
                setattr(model, key, value)
        self.db.commit()
        self.db.refresh(model)
        return model
