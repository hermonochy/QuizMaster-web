from typing import Union, Dict, List
from glob import glob
from fastapi import FastAPI
import random
import aiofiles
from fastapi.middleware.cors import CORSMiddleware
from fuzzywuzzy import fuzz
import json

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


@app.get("/items/{item_id}", response_model=Dict)
async def read_item(item1_id: Union[float, None] = 1.0, item2_id: Union[float, None] = 1.0) -> Dict:
    return {"item1*item2": item1_id * item2_id}


@app.get("/randomQuiz", response_model=Dict)
async def get_quiz() -> Dict:
    """Get a random quiz from all available quiz files"""
    quizfiles = glob('./quizzes/**/*.json', recursive=True)
    quizfile = random.choice(quizfiles)
    
    async with aiofiles.open(quizfile, 'r') as f:
        contents = await f.read()
    
    return {"randomQuiz": contents}


def search_str_in_file(file_path: str, word: str) -> bool:
    """Search for a word in a file using fuzzy matching"""
    try:
        with open(file_path, 'r', errors="ignore") as file:
            content = file.read().lower()
            words = content.split()

            if word.lower() in content:
                return True
            
            for w in words:
                if fuzz.ratio(w, word.lower()) > 70:
                    return True
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return False


async def load_quiz_file(file_path: str) -> Dict:
    """Load and parse a quiz file"""
    try:
        async with aiofiles.open(file_path, 'r') as f:
            contents = await f.read()
            return json.loads(contents)
    except Exception as e:
        print(f"Error loading quiz file {file_path}: {e}")
        return None


@app.get("/searchQuiz", response_model=Dict)
async def search_quiz(query: str) -> Dict:
    """Search for quizzes based on a search term"""
    if not query or len(query.strip()) == 0:
        return {"success": False, "message": "Search query cannot be empty", "results": []}
    
    quizfiles = glob('./Quizzes/**/*.json', recursive=True)
    
    matching_files = []
    for file in quizfiles:
        if search_str_in_file(file, query):
            matching_files.append(file)
    
    if not matching_files:
        return {"success": False, "message": "No quizzes found matching your search", "results": []}
    
    # Load all matching quizzes
    results = []
    for file_path in matching_files:
        quiz_data = await load_quiz_file(file_path)
        if quiz_data:
            results.append({
                "title": quiz_data.get('title', 'Untitled Quiz'),
                "filePath": file_path,
                "quiz": quiz_data
            })
    
    return {"success": True, "message": f"Found {len(results)} quiz(zes)", "results": results}


@app.get("/getQuizByPath", response_model=Dict)
async def get_quiz_by_path(path: str) -> Dict:
    """Get a specific quiz by file path"""
    try:
        async with aiofiles.open(path, 'r') as f:
            contents = await f.read()
        
        return {"success": True, "randomQuiz": contents}
    except Exception as e:
        return {"success": False, "message": f"Error loading quiz: {str(e)}"}