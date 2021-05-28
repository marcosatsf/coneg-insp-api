from typing import Optional
from fastapi import FastAPI, File, Body, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from db_transactions import PsqlPy
import pandas as pd
import shutil
import uvicorn

class Req_insp(BaseModel):
    is_with_mask: bool
    ts: int
    location: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    # db = PsqlPy()
    # db.connect()
    # dfCad = pd.read_csv('files/cadastros.csv')
    # for _, row in dfCad.iterrows():
    #     db.insert_reg(
    #         id=row['identificacao'],
    #         nome=row['nome'],
    #         email=row['email'],
    #         telefone=row['telefone']
    #     )
    # db.disconnect()
    return {"message": "Hello World!"}

@app.post("/found")
async def found_face_withorwithout(
    is_with_mask: bool = Form(...),
    ts: int = Form(...),
    location: str = Form(...),
    file_uploaded: UploadFile = File(None)
):
    # Receive request and save frame
    if file_uploaded:
        with open('test.jpg', 'wb') as buffer:
            shutil.copyfileobj(file_uploaded.file, buffer)
    return {
        'mask':is_with_mask, 
        'ts':ts,
        'loc':location}

# if __name__ == "__main__":
#     uvicorn.run(app, port=6000, host='0.0.0.0')
