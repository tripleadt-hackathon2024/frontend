from uuid import uuid4

from ollama import Client
from utils import save_file
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from transcribe import transcribe_text
from obstacle_detection import detection_object, generate_object_detection_prompt

app = FastAPI()
client = Client(host='https://apiollama.pandakewt.net')

userContent = {}

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


@app.post('/detectObject')
async def detect_object(file: UploadFile):
    dest = save_file(['video/webm'], file)
    cords_obj = detection_object(dest)
    prompt = generate_object_detection_prompt(cords_obj)
    result = client.generate(model='llama3:8b', prompt=prompt, stream=False)
    return result


# @app.post('/transcribe')
# async def transcribe(file: UploadFile):
#     dest = save_file(['video/webaskdamdmsamm'], file)
#     return {'filename': file.filename, 'data': transcribe_text(dest)}


@app.get('/generateUserID')
async def generate_user_id():
    rand_uid = uuid4().hex
    while rand_uid in userContent.keys():
        rand_uid = uuid4().hex
    userContent[rand_uid] = {'chat': [{'role': 'system', 'content': ''}]}
    return {'key': rand_uid}


class ChatData(BaseModel):
    key: str
    message: str


@app.post('/chat')
async def generate_chat(data: ChatData):
    if data.key not in userContent.keys():
        raise HTTPException(status_code=400, detail='UserID not found')
    if len(data.message) == 0:
        raise HTTPException(status_code=400, detail='Message invalid')
    userContent[data.key]['chat'].append({'role': 'user', 'content': data.message})
    response = client.chat(model='llama3:8b', messages=userContent[data.key]['chat'], stream=False)
    userContent[data.key]['chat'].append(response["message"])
    return userContent


class UserData(BaseModel):
    key: str


@app.post('/checkUserID')
async def generate_chat(data: UserData):
    if data.key not in userContent.keys():
        raise HTTPException(status_code=400, detail='UserID not found')
    return
