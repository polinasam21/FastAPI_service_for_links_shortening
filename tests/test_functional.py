import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, SessionLocal
from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


TEST_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/test_{DB_NAME}"


@pytest.fixture()
def test_db():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def test_client(test_db):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)

    def test_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = test_get_db

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def create_test_user(test_client):
    response = test_client.post("/register", json={"username": "test_user", "email": "test_user@yandex.ru", "password": "test_user_password"})
    assert response.status_code == 200
    return response.json()


@pytest.fixture()
def get_token(test_client, create_test_user):
    response = test_client.post("/token", data={"username": "test_user", "password": "test_user_password"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def create_test_short_link(test_client):
    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/", "custom_alias": "goo"})
    assert response.status_code == 200
    assert response.json() == {"message" : "Link successfully created", "original_url" : "https://www.google.com/", "short_code": "goo"}
    return response.json()


def test_register_user(test_client):
    response = test_client.post("/register", json={"username": "new_user", "email": "new_user@yandex.ru", "password": "new_user_password"})
    response_json = response.json()
    assert response.status_code == 200
    assert "message" in response_json
    assert response_json["message"] == "User created successfully"


def test_register_user_with_exist_user(test_client):
    response = test_client.post("/register", json={"username": "new_user", "email": "new_user@yandex.ru", "password": "new_user_password"})
    response_json = response.json()
    assert response.status_code == 200
    assert "message" in response_json
    assert response_json["message"] == "User created successfully"

    response = test_client.post("/register", json={"username": "new_user", "email": "new_user@yandex.ru", "password": "new_user_password"})
    assert response.status_code == 400


def test_login_user(test_client, create_test_user):
    response = test_client.post("/token", data={"username": "test_user", "password": "test_user_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_with_error(test_client, create_test_user):
    response = test_client.post("/token", data={"username": "test_user_1", "password": "test_user_password_1"})
    assert response.status_code == 401


def test_create_short_link_with_custom_alias(test_client):
    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/", "custom_alias": "goo"})
    assert response.status_code == 200
    assert response.json() == {"message" : "Link successfully created", "original_url" : "https://www.google.com/", "short_code": "goo"}


def test_create_short_link_without_custom_alias(test_client):
    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/"})
    response_json = response.json()
    assert response.status_code == 200
    assert "message" in response_json
    assert  response_json["message"] == "Link successfully created"
    assert "original_url" in response_json
    assert response_json["original_url"] == "https://www.google.com/"
    assert "short_code" in response_json
    assert len(response_json["short_code"]) == 6


def test_create_short_link_with_existing_link(test_client):
    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/", "custom_alias": "goo"})
    assert response.status_code == 200
    assert response.json() == {"message" : "Link successfully created", "original_url" : "https://www.google.com/", "short_code": "goo"}

    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/", "custom_alias": "goo"})
    assert response.status_code == 400


def test_redirect(test_client, create_test_short_link):
    response = test_client.get("/links/goo")
    assert response.status_code == 200


def test_redirect_with_not_existing_link(test_client, create_test_short_link):
    response = test_client.get("/links/some_link")
    assert response.status_code == 404


def test_update_short_link(test_client, create_test_short_link, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.put(f"/links/goo", json={"short_code_old": "goo", "short_code_new": "gl"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message" : "short_code updated successfully", "original_url" : "https://www.google.com/", "short_code" : "gl"}


def test_update_short_link_with_not_existing_link(test_client, create_test_short_link, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.put(f"/links/some_link", json={"short_code_old": "some_link", "short_code_new": "gl"}, headers=headers)
    assert response.status_code == 404


def test_delete_short_link(test_client, create_test_short_link, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.delete(f"/links/goo", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Link successfully deleted"}


def test_delete_short_link_unauthorized(test_client, create_test_short_link):
    response = test_client.delete("/links/goo")
    assert response.status_code == 401


def test_delete_short_link_with_not_existing_link(test_client, create_test_short_link, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.delete(f"/links/some_link", headers=headers)
    assert response.status_code == 404


def test_search_link(test_client, create_test_short_link):
    response = test_client.get("/links/search/link?original_url=https://www.google.com/")
    assert response.status_code == 200
    assert response.json() == {"short_code": "goo"}


def test_search_link_with_not_existing_link(test_client, create_test_short_link):
    response = test_client.get("/links/search/link?original_url=https://www.somesite.com/")
    assert response.status_code == 404


def test_get_link_stats(test_client, create_test_short_link):
    response = test_client.get("/links/goo/stats")
    response_json = response.json()
    assert response.status_code == 200
    assert "original_url" in response_json
    assert "short_code" in response_json
    assert "created_at" in response_json
    assert "last_accessed_at" in response_json
    assert "expires_at" in response_json
    assert "access_count" in response_json


def test_get_link_stats_with_not_existing_link(test_client, create_test_short_link):
    response = test_client.get("/links/some_link/stats")
    assert response.status_code == 404


def test_remove_unused_links(test_client, create_test_short_link, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.delete("/links/remove_unused/links", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"Deleted 1 unused links"}


def test_remove_unused_links_without_unused_links(test_client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = test_client.delete("/links/remove_unused/links", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "There are no unused links"}


def test_get_expired_links(test_client):
    response = test_client.post("/links/shorten", json={"original_url": "https://www.google.com/", "custom_alias": "goo", "expires_at": "2025-03-25 00:00"})
    assert response.status_code == 200
    assert response.json() == {"message": "Link successfully created", "original_url": "https://www.google.com/", "short_code": "goo"}

    response = test_client.get("/links/expired/links")
    response_json = response.json()
    assert response.status_code == 200
    assert len(response_json) == 1
    assert "original_url" in response_json[0]
    assert "short_code" in response_json[0]
    assert "created_at" in response_json[0]
    assert "expires_at" in response_json[0]


