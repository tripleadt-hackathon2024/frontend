import logging
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGenerate:
    @staticmethod
    def test_generate_websocket():
        with client.websocket_connect('/ws') as websocket:
            get_key_response = client.get('/generateUserID')
            websocket.send_json({
                'command': 'generateChat',
                'key': get_key_response.json()['key'],
                'message': 'Hello tell me about you'
            })
            message = ''
            while True:
                response = websocket.receive_json()
                if 'error' in response:
                    logging.error(response['error'])
                    print(response['error'])
                    assert False
                if 'status' in response:
                    break
                else:
                    message += response['content']
                    logging.info(response['content'])
            logging.info(message)
            assert True
