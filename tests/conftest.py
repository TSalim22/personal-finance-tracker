import os
import pytest
from app import create_app
from auth import db

@pytest.fixture
def app():
    application = create_app({'TESTING':True,'SECRET_KEY':'test-only-key','WTF_CSRF_ENABLED':False,
        'SQLALCHEMY_DATABASE_URI':os.getenv('TEST_DATABASE_URL','sqlite://'),
        'STRIPE_SECRET_KEY':'','STRIPE_WEBHOOK_SECRET':'','STRIPE_PRICE_ID':''})
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def logged_in(client):
    response = client.post('/register',data={'username':'student','password':'student-test-pass'})
    assert response.status_code==302
    return client
