from typing import Union, Dict
from glob import glob
from fastapi import FastAPI
import random
import aiofiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}",response_model=Dict)
async def read_item(item1_id: Union[float,None]=1.0, item2_id: Union[float,None]=1.0)->Dict:
    return {"item1*item2": item1_id*item2_id}


@app.get("/randomQuiz",response_model=Dict)
async def get_quiz()->Dict:

    #TODO glob all quiz jsons
    quizfiles = glob('./quizzes/**/*.json', recursive=True)
    quizfile = random.choice(quizfiles)
    
    async with aiofiles.open(quizfile, 'r') as f:
        contents = await f.read()
    
    return {"randomQuiz": contents}
