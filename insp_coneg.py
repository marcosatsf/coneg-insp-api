from typing import Optional
from fastapi import FastAPI, File, Body, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import request_manager as req_m
from datetime import datetime
from time import time
import pandas as pd
import os
import shutil
import uvicorn

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
    ts: int = Form(...),
    location: str = Form(...),
    file_uploaded: UploadFile = File(None)
):
    """
    Information request from inspector, containing some useful
    metrics data. 

    Args:
        ts (int): Timestamp from the moment of inspector's 
        request.
        location (str): Location from which inspector is sending 
        request.
        file_uploaded (UploadFile): Frame captured using mask or 
        not.

    Returns:
        (dict): Response with timestamp, location and is frame
        was sent by the inspector side.
    """
    # Transform to timestamp acceptable to Postgres
    dt = str(datetime.fromtimestamp(ts))
    # Receive request and save frame
    if file_uploaded:
        if not os.path.exists('shr-data/registry/'):
            os.mkdir('shr-data/registry/')
        
        file_name = f"./shr-data/registry/{int(time())}.jpg"
        with open(file_name, 'wb') as buffer:
            shutil.copyfileobj(file_uploaded.file, buffer)
        # Spawns thread to analyze this image
        req_m.multiprocess_recognition(location, dt, file_name)
    else:
        req_m.ins_clean_request(location, dt)

    return {
        'ts':dt,
        'loc':location,
        'file_sent': bool(file_uploaded)
        }

if __name__ == "__main__":
    uvicorn.run(app, port=6000, host='0.0.0.0')
