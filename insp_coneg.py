from typing import Optional
from fastapi import FastAPI, File
from fastapi.datastructures import UploadFile
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
    request: Req_insp,
    files: Optional[UploadFile] = File(...)
):
    # Receive request and parse as JSON -> dict
    req_conv = request.dict()
    print(req_conv)
    
    return {"received_api": req_conv}

# if __name__ == "__main__":
#     uvicorn.run(app, port=6000, host='0.0.0.0')
