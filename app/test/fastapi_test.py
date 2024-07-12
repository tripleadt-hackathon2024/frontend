from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestUserID:
    @staticmethod
    def test_generate_user_id():
        response = client.get('/generateUserID')
        assert response.status_code == 200
        assert type(response.json()['key']) == str

    @staticmethod
    def test_check_user_id_invalid():
        check_key_responses = client.post('/checkUserID', json={
            'key': 'notARealKey'
        })
        assert check_key_responses.status_code == 400

    @staticmethod
    def test_check_user_id_valid():
        get_key_response = client.get('/generateUserID')
        check_key_responses = client.post('/checkUserID', json={'key': get_key_response.json()['key']})
        assert check_key_responses.status_code == 200


class TestChat:
    @staticmethod
    def test_chat_invalid_chat_key():
        chat_response = client.post('/chat', json={'key': 'notARealKey', 'message': 'hi'})
        assert chat_response.status_code == 400

    @staticmethod
    def test_chat_invalid_message():
        chat_key = client.get('/generateUserID').json()["key"]
        chat_response = client.post('/chat', json={'key': chat_key, 'message': ''})
        assert chat_response.status_code == 400

    @staticmethod
    def test_chat_valid():
        chat_key = client.get('/generateUserID').json()["key"]
        chat_response = client.post('/chat', json={'key': chat_key, 'message': 'Hi'})
        assert chat_response.status_code == 200


class TestDetectObject:
    @staticmethod
    def test_detect_object_invalid_mime_type():
        client.post('/detectObject')
