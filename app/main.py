import base64
from typing import List
from uuid import uuid4

from fastapi import FastAPI, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from ollama import AsyncClient

from obstacle_detection import detection_object, generate_object_detection_prompt
# from text_to_speech import text_to_speach
from utils import save_file

app = FastAPI()
client = AsyncClient(host='https://apiollama.pandakewt.net')

userContent = {
    'test': [{'role': 'system', 'content': ''}]
}

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ErrorResponse(BaseModel):
    message: str


class ChatResponse(BaseModel):
    role: str
    content: str


class UserData(BaseModel):
    key: str


class GenerateUserIDResponse(BaseModel):
    key: str


class GenerateChatRequest(UserData):
    message: str


class GenerateChatResponse(BaseModel):
    message: ChatResponse
    audio: str


class GenerateSpeachRequest(BaseModel):
    message: str


@app.post('/detectObject')
def detect_object(file: UploadFile):
    dest = save_file(['video/webm'], file)
    cords_obj, text_result = detection_object(dest)
    prompt = generate_object_detection_prompt(cords_obj, text_result)
    result = client.generate(model='gemma', prompt=prompt, stream=False)
    return result


@app.get('/generateUserID', response_model=GenerateUserIDResponse, status_code=200)
def generate_user_id():
    rand_uid = uuid4().hex
    while rand_uid in userContent.keys():
        rand_uid = uuid4().hex
    userContent[rand_uid] = [{'role': 'system', 'content': ''}]
    return {'key': rand_uid}


@app.post('/generateChat', response_model=GenerateChatResponse, responses={400: {'model': ErrorResponse}})
async def generate_chat(data: GenerateChatRequest):
    if data.key not in userContent.keys():
        return JSONResponse({'message': 'UserID not found'}, status_code=400)
    if len(data.message) == 0:
        return JSONResponse({'message': 'Message cannot be empty'}, status_code=400)
    userContent[data.key].append({'role': 'user', 'content': data.message})
    response = await client.chat(model='llama3:8b', messages=userContent[data.key], stream=False)
    userContent[data.key].append(response['message'])
    # encode_string = base64.b64encode(open(text_to_speach(text=response['message']['content']), "rb").read())
    return {'message': response['message'], 'audio': ''}


@app.post('/getChatHistory', response_model=List[ChatResponse], responses={400: {'model': ErrorResponse}})
def generate_chat_history(data: UserData):
    if data.key not in userContent.keys():
        return JSONResponse(status_code=400, content={400: {'message': 'UserID not found'}})
    return userContent[data.key][1::]


@app.post('/checkUserID', responses={400: {'model': ErrorResponse}})
def check_user_id(data: UserData):
    if data.key not in userContent.keys():
        return JSONResponse(status_code=400, content={400: {'message': 'UserID not found'}})
    return


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data['command'] == 'generateChat':
                if data['key'] not in userContent.keys():
                    await websocket.send_json({'message': 'UserID not found'})
                    continue
                if data['message'] == '':
                    await websocket.send_json({'message': 'Message cannot be empty'})
                    continue

                userContent[data['key']].append({'role': 'user', 'content': data['message']})
                stream = await client.chat(model='llama3:8b', messages=userContent[data['key']], stream=True)
                userContent[data['key']].append({'role': 'assistant', 'content': ''})
                async for chunk in stream:
                    if 'content' in chunk['message']:
                        userContent[data['key']][-1]['content'] += chunk['message']['content']
                    await websocket.send_json(chunk['message'])

    except Exception as e:
        print(e)
        await websocket.send_json({'error': str(e)})
        await websocket.close(1000, str(e))
