"""Интеграционные тесты HTTP + настоящая временная SQLite, не моки ORM."""
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database import Base, get_db, make_engine
from backend.app.models import Category, Part
from backend.app.seed import init_db

VALID = {"name": "Салонный фильтр", "description": "Очищает воздух в салоне автомобиля от пыли.", "article": "TEST-001", "price": "790.50", "category_id": 1}

@pytest.fixture()
def db_engine(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_db(engine)
    yield engine
    engine.dispose()

@pytest.fixture()
def client(db_engine):
    sessions = sessionmaker(bind=db_engine, expire_on_commit=False)
    def override_db():
        with sessions() as session:
            yield session
    app.dependency_overrides[get_db] = override_db
    # lifespan не запускаем: тестовые таблицы созданы fixture и не затрагивают рабочую БД.
    with TestClient(app, raise_server_exceptions=False) as http:
        yield http
    app.dependency_overrides.clear()


def test_complete_crud_and_database(client, db_engine):
    assert len(client.get('/api/parts').json()) == 6
    response = client.post('/api/parts', json=VALID)
    assert response.status_code == 201
    item = response.json(); item_id = item['id']
    assert item['price'] == '790.50'
    assert item['category']['name'] == 'Двигатель'
    assert response.headers['Location'] == f'/api/parts/{item_id}'
    assert item['created_at'].endswith('Z')
    with db_engine.connect() as db:
        assert db.execute(text('SELECT article FROM parts WHERE id=:id'), {'id':item_id}).scalar_one() == 'TEST-001'
    assert client.get(f'/api/parts/{item_id}').json()['article'] == 'TEST-001'
    changed = client.patch(f'/api/parts/{item_id}', json={'price':'849.90','category_id':2})
    assert changed.status_code == 200
    assert changed.json()['price'] == '849.90'
    assert changed.json()['category']['name'] == 'Тормоза'
    assert changed.json()['name'] == VALID['name']
    deleted = client.delete(f'/api/parts/{item_id}')
    assert deleted.status_code == 204 and deleted.content == b''
    assert client.get(f'/api/parts/{item_id}').status_code == 404
    with db_engine.connect() as db:
        assert db.execute(text('SELECT COUNT(*) FROM parts WHERE id=:id'), {'id':item_id}).scalar_one() == 0

@pytest.mark.parametrize('method', ['get','patch','delete'])
def test_not_found(client, method):
    kwargs = {'json':{'price':'800.00'}} if method == 'patch' else {}
    assert getattr(client,method)('/api/parts/999999', **kwargs).status_code == 404

@pytest.mark.parametrize('change', [
    {'name':''}, {'name':'  '}, {'name':'a'*61}, {'description':'коротко'},
    {'description':'a'*241}, {'article':'BAD 123'}, {'article':'abc'},
    {'price':-1}, {'price':0}, {'price':'1000000.01'}, {'price':'1.001'},
    {'price':'NaN'}, {'price':'Infinity'}, {'category_id':0}, {'category_id':'abc'},
    {'category_id':1.5}, {'name':None}, {'unexpected':'value'},
    {'image_url':'javascript:alert(1)'}, {'parameter':'a'*121}
])
def test_create_validation(client, change):
    assert client.post('/api/parts', json={**VALID, **change}).status_code == 422

@pytest.mark.parametrize('field', list(VALID))
def test_required_fields(client, field):
    data = dict(VALID); data.pop(field)
    assert client.post('/api/parts', json=data).status_code == 422

@pytest.mark.parametrize('data', [{'price':None}, {'name':None}, {'category_id':None}, {'article':'bad code'}, {'extra':1}, {'price':'1.001'}])
def test_patch_validation(client, data):
    assert client.patch('/api/parts/1', json=data).status_code == 422


def test_empty_patch_and_bad_json(client):
    assert client.patch('/api/parts/1', json={}).status_code == 400
    response = client.post('/api/parts', content='{"name":', headers={'Content-Type':'application/json'})
    assert response.status_code == 400


def test_duplicate_article_normalization_and_rollback(client):
    assert client.post('/api/parts', json={**VALID, 'article':' test-001 '}).status_code == 201
    assert client.post('/api/parts', json=VALID).status_code == 400
    assert client.patch('/api/parts/1', json={'article':'test-001'}).status_code == 400
    # После ошибки транзакция откатывается; следующий корректный запрос проходит.
    assert client.patch('/api/parts/1', json={'price':'501.25'}).status_code == 200


def test_unknown_category_and_categories(client):
    assert len(client.get('/api/categories').json()) == 6
    assert client.get('/api/categories/1').json()['slug'] == 'engine'
    assert client.get('/api/categories/999').status_code == 404
    assert client.post('/api/parts', json={**VALID, 'category_id':999}).status_code == 400
    assert client.patch('/api/parts/1', json={'category_id':999}).status_code == 400


def test_database_constraints(db_engine):
    with db_engine.connect() as connection:
        assert connection.execute(text('PRAGMA foreign_keys')).scalar_one() == 1
    statements = [
        "UPDATE parts SET price=-1 WHERE id=1",
        "UPDATE parts SET price=1.001 WHERE id=1",
        "UPDATE parts SET name=NULL WHERE id=1",
        "UPDATE parts SET category_id=999 WHERE id=1",
        "UPDATE parts SET article='AP-BR-002' WHERE id=1",
        "DELETE FROM categories WHERE id=1",
    ]
    for statement in statements:
        with pytest.raises(IntegrityError):
            with db_engine.begin() as connection:
                connection.execute(text(statement))


def test_delete_all_then_restart_does_not_reseed(client, db_engine):
    for item in client.get('/api/parts').json():
        assert client.delete(f"/api/parts/{item['id']}").status_code == 204
    init_db(db_engine)
    assert client.get('/api/parts').json() == []
    assert len(client.get('/api/categories').json()) == 6


def test_openapi_and_local_swagger_assets(client):
    spec = client.get('/openapi.json').json()
    assert spec['info']['version'] == '3.0.0'
    assert {'get','post'} <= set(spec['paths']['/api/parts'])
    assert {'get','patch','delete'} <= set(spec['paths']['/api/parts/{part_id}'])
    assert '201' in spec['paths']['/api/parts']['post']['responses']
    assert '422' in spec['paths']['/api/parts']['post']['responses']
    assert '204' in spec['paths']['/api/parts/{part_id}']['delete']['responses']
    assert 'examples' in spec['components']['schemas']['PartCreate']
    assert client.get('/docs').status_code == 200
    assert client.get('/swagger-assets/swagger-ui-bundle.js').status_code == 200
    assert client.get('/redoc').status_code == 200
    assert client.get('/').status_code == 200
    assert client.get('/css/style.css').status_code == 200


def test_cors_for_optional_separate_frontend(client):
    headers={'Origin':'http://127.0.0.1:5500','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'}
    response = client.options('/api/parts', headers=headers)
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://127.0.0.1:5500'
    denied = client.options('/api/parts', headers={**headers,'Origin':'https://example.invalid'})
    assert denied.status_code == 400


def test_server_error_does_not_expose_sql(client):
    def broken_db():
        raise OperationalError('SECRET SQL', {}, Exception('SECRET CONFIG'))
        yield
    app.dependency_overrides[get_db] = broken_db
    response = client.get('/api/parts')
    assert response.status_code == 500
    assert 'SECRET' not in response.text


def test_persistence_across_new_processes(tmp_path):
    url = f"sqlite:///{tmp_path / 'restart.db'}"
    env = {**os.environ, 'DATABASE_URL':url}
    first = '''
from backend.app.database import engine, SessionLocal
from backend.app.seed import init_db
from backend.app import crud
from backend.app.schemas import PartCreate
init_db(engine)
with SessionLocal() as db:
    crud.create_part(db, PartCreate(name="Салонный фильтр", description="Проверка сохранения после перезапуска процесса.", article="PERSIST-001", price="123.45", category_id=1))
engine.dispose()
'''
    second = '''
from backend.app.database import engine, SessionLocal
from backend.app.seed import init_db
from sqlalchemy import text
init_db(engine)
with engine.connect() as db:
    print(db.execute(text("SELECT price FROM parts WHERE article='PERSIST-001'")).scalar_one())
'''
    subprocess.run([sys.executable,'-c',first],env=env,check=True,capture_output=True,text=True)
    result = subprocess.run([sys.executable,'-c',second],env=env,check=True,capture_output=True,text=True)
    assert Decimal(result.stdout.strip()) == Decimal('123.45')
