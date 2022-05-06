"""Service test cases."""
from sqlite3 import IntegrityError
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Column, Integer, String

from app.database import Base
from app.services.base import Service, NotFoundError
from app.services.user import UserService, EmailAlreadyRegistredError


class DummyModel(Base):  # pylint: disable=too-few-public-methods
    """Dummy model."""

    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class DummyService(Service[DummyModel]):
    """Dummy service."""

    __model__ = DummyModel


@pytest.fixture(name="db")
def fixture_db():
    """Fixture for a database session."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = session_local()
    Base.metadata.create_all(engine)
    yield session
    Base.metadata.drop_all(engine)
    session.close()


@pytest.fixture(name="service")
def fixture_service(db):
    """Fixture for a service."""
    service = DummyService(db=db)
    return service


@pytest.fixture(name="user_service")
def fixture_user_service(db):
    """Fixture for a user service."""
    service = UserService(db=db)
    return service


def test_service_raises_not_implemented_error(db):
    """Test that the service raises a NotImplementedError."""
    with pytest.raises(NotImplementedError):
        Service(db=db)


def test_dummy_service_create_model(service: DummyService):
    """Test that the UserService.create_model() method works."""
    model = service.create_model(name="Dummy")
    assert hasattr(model, "name")
    assert model.name == "Dummy", "The model name should be 'Dummy'"


def test_dummy_service_save_model(service: DummyService):
    """Test that the UserService.get_model() method works."""
    model = service.create_model(name="Dummy")
    result = service.save(model)
    assert model.name == result.name, "The model name should be 'Dummy'"
    assert result.id is not None, "The model should have an id"
    assert isinstance(result.id, int), "The id should be an integer"


def test_dummy_service_get_one_model(service: DummyService):
    """Test that the UserService.get_model() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    result = service.get_one(name="Dummy")
    assert result.name == "Dummy", "The model name should be 'Dummy'"


def test_dummy_service_get_one_returns_none(service: DummyService):
    """Test that the UserService.get_model() method works."""
    result = service.get_one(name="Dummy")
    assert result is None, "The result should be None"


def test_dummy_service_raise_not_found_error(service: DummyService):
    """Test that the UserService.get_model() method works."""
    with pytest.raises(NotFoundError) as exec_info:
        service.get_one_or_raise(name="Dummy")
    assert exec_info.value.params == {"name": "Dummy"}, "The params should be 'Dummy'"


def test_dummy_service_get_by_id(service: DummyService):
    """Test that the UserService.get_model() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    result = service.get_by_id(model.id)
    assert result.name == "Dummy", "The model name should be 'Dummy'"


def test_dummy_service_get_by_id_raises_not_found_error(service: DummyService):
    """Test that the UserService.get_model() method works."""
    with pytest.raises(NotFoundError):
        service.get_by_id(1)


def test_dummy_service_get_all_when_1_registry_was_inserted(service: DummyService):
    """Test that the UserService.get_all() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    result = list(service.get_all())
    assert len(result) == 1, "The result should have one element"


def test_dummy_service_get_all_when_0_registry_was_inserted(service: DummyService):
    """Test that the UserService.get_all() method works."""
    result = list(service.get_all())
    assert len(result) == 0, "The result should be empty"


def test_dummy_service_get_all_when_2_registries_were_inserted(service: DummyService):
    """Test that the UserService.get_all() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    model = service.create_model(name="Dummy2")
    service.save(model)
    result = list(service.get_all())
    assert len(result) == 2, "The result should have two elements"


def test_dummy_service_delete_model(service: DummyService):
    """Test that the UserService.delete_model() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    service.delete(model.id)
    with pytest.raises(NotFoundError):
        service.get_by_id(model.id)


def test_dummy_service_delete_model_raises_not_found_error(service: DummyService):
    """Test that the UserService.delete_model() method works."""
    with pytest.raises(NotFoundError):
        service.delete(1)


def test_dummy_service_update_model(service: DummyService):
    """Test that the UserService.update_model() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    model.name = "Dummy2"
    service.update(model)
    model = service.get_by_id(model.id)
    assert model.name == "Dummy2", "The model name should be 'Dummy2'"


def test_dummy_service_update_model_raises_not_found_error(service: DummyService):
    """Test that the UserService.update_model() method works."""
    with pytest.raises(NotFoundError):
        model = service.create_model(id=1, name="Dummy")
        service.update(model)


def test_dummy_service_default_params(service: DummyService):
    """Test that the UserService.default_params() method works."""
    service.update_default_params(name="Dummy")
    model = service.create_model()
    service.save(model)
    assert model.name == "Dummy", "The model name should be 'Dummy'"


def test_dummy_service_default_params_can_be_queried(service: DummyService):
    """Test that the UserService.default_params() method works."""
    service.update_default_params(name="Dummy")
    service.save(service.create_model())
    model = service.get_one()
    assert model.name == "Dummy", "The model name should be 'Dummy'"


def test_dummy_service_default_params_can_be_overriden(service: DummyService):
    """Test that the UserService.default_params() method works."""
    service.update_default_params(name="Dummy")
    model = service.create_model(name="Dummy2")
    service.save(model)
    assert model.name == "Dummy2", "The model name should be 'Dummy2'"


def test_dummy_service_count_when_no_registries_were_inserted(service: DummyService):
    """Test that Service.count() method works."""
    assert service.count() == 0, "The count should be 0"


def test_dummy_service_count_when_1_registry_was_inserted(service: DummyService):
    """Test that the UserService.count() method works."""
    model = service.create_model(name="Dummy")
    service.save(model)
    result = service.count()
    assert result == 1, "The result should be 1"


def test_dummy_service_count_when_100_registries_was_inserted(service: DummyService):
    """Test that the UserService.count() method works."""
    for i in range(100):
        service.save(service.create_model(name=f"Dummy {i}"))
    result = service.count()
    assert result == 100, "The result should be 100"


def test_EmailAlreadyRegistredError_message():
    """Test that the EmailAlreadyRegisteredError has the correct message."""
    with pytest.raises(EmailAlreadyRegistredError) as exec_info:
        raise EmailAlreadyRegistredError("fake@mail.com")
    assert (
        exec_info.value.args[0] == "User with email fake@mail.com already exists."
    ), "The message should be 'User with email fake@mail.com aleady exists.'"


def test_user_service_create_an_already_registered_email(user_service: UserService):
    """Test that the UserService.save() method works."""
    user_service.save(user_service.create_model(name="Fake", email="fake@mail.com"))
    with pytest.raises(EmailAlreadyRegistredError):
        user_service.save(user_service.create_model(name="Fake2", email="fake@mail.com"))


def test_user_service_update_with_an_different_and_already_registered_email(
    user_service: UserService,
):
    """Test that the UserService.update() method works."""
    user_service.save(user_service.create_model(name="Fake", email="fake@mail.com"))
    user = user_service.save(user_service.create_model(name="Fake2", email="fake2@mail.com"))
    user.email = "fake@mail.com"
    with pytest.raises(EmailAlreadyRegistredError):
        user_service.update(user)


def test_user_service_update_with_same_email_and_same_id(user_service: UserService):
    """Test that the UserService.update() method works."""
    user = user_service.save(user_service.create_model(name="Fake", email="fake@mail.com"))
    user.name = "New Fake"
    user_service.update(user)


def test_user_service_has_email(user_service: UserService):
    """Test that the UserService.has_email() method works."""
    user_service.save(user_service.create_model(name="Fake", email="fake@mail.com"))
    assert user_service.has_email(email="fake@mail.com"), "The email should exist"
