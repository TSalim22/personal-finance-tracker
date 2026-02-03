from app import create_app
from auth import db,User

def test_accounts_and_password_hashing(client,app):
    assert client.get('/').status_code==302
    assert client.post('/register',data={'username':'student','password':'short'}).status_code==400
    assert client.post('/register',data={'username':'student','password':'test-password'}).status_code==302
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.password_hash != 'test-password'
    client.post('/logout')
    assert client.post('/login',data={'username':'student','password':'wrong'}).status_code==400
    assert client.post('/login',data={'username':'student','password':'test-password'}).status_code==302
    assert client.post('/register',data={'username':'student','password':'test-password'}).status_code==400

def test_csrf_blocks_missing_token():
    app = create_app({'TESTING':True,'SQLALCHEMY_DATABASE_URI':'sqlite://','SECRET_KEY':'csrf-test-key'})
    response = app.test_client().post('/register',data={'username':'student','password':'test-password'})
    assert response.status_code==400
