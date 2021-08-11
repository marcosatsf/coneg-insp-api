from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from db_transactions import PsqlPy
from dotenv import load_dotenv
import face_recognition
import numpy as np
from glob import glob
import time
import os
import yagmail
import yaml

def multiprocess_recognition(
        location: str, 
        ts : str, 
        f_image_jpg : str
    ):
    """
    Tries to recognize a face and then register a new line
    into the fact table.

    Args:
        location (str): Location configured on Inspector.
        ts (str): Timestamp using date and time (no time zone).
        f_image_jpg (str): Filename including relative path to the
        image which we received on api request.
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(which_face, f_image_jpg)

        db = PsqlPy()
        # Returns the pesid from coneg.cadastros
        pesid = future.result()
        if pesid:
            # Status 2 -> not mask & registered
            data_notific = load_notification_config()
            if data_notific:
                person = db.select_query(pesid)
                if person:
                    notify(data_notific, person)
                    db.update_query(True, pesid)
                else:
                    print(f'Person [{person}] already notified!')

            # Status 2 -> not mask & registered
            db.insert_row(
                local=location,
                ts=ts,
                status=2,
                pessoa=pesid
            )
            # file_name = f"./shr-data/registry/{int(time())}.jpg"
            os.rename(f_image_jpg, f'./shr-data/registry/{pesid}_{ts}.jpg')
        else:
            # Status 1 -> not mask & not registered
            db.insert_row(
                local=location,
                ts=ts,
                status=1
            )           
            # Remove temporary file received from inspector
            os.remove(f_image_jpg)
        
        db.disconnect()


def which_face(image_jpg : str) -> str:
    """
    Verifies if it's (un)known face, returning the
    value to it. If a known face is detected, returns the
    ID related to that face. If a unknown face is detected,
    returns an empty string meaning that person is not registered
    on system.

    Args:
        image_jpg (str): Filename including relative path to the
        image which we received on api request.

    Returns:
        file_name (str): String ID to known face or empty string.
    """
    # List of known faces encodings
    faces = []
    # List of known faces image paths
    faces_id = []

    for path in glob('./shr-data/faces/*.jpg'):
        image = face_recognition.load_image_file(path)
        faces_id.append(path)
        try:
            faces.append(face_recognition.face_encodings(image)[0])
        except IndexError:
            faces_id.pop()
            continue

    image = face_recognition.load_image_file(image_jpg)
    try:
        unknown = face_recognition.face_encodings(image)[0]

        results = face_recognition.compare_faces(faces, unknown)
        results = np.nonzero(results)[0]
    except IndexError:
        results = []
    
    # If there's exact one person related to that captured frame
    if len(results) == 1:
        # results = ['./shr-data/faces/teste.jpg']
        file_name = faces_id[results[0]].split('/')[-1].split('.')[0]
    else:
        file_name = ''

    return file_name


def load_notification_config(retries : int = 3) -> Dict[str, str]:
    """
    Reads configuration done by admin. Retries N times until
    fails to load and proceed without notify. Default to `retries`
    is 3.

    Returns:
        dict: method and message configured by admin.
    """
    for e in range(retries):
        try:
            with open(f'./shr-data/config_notificacao.yaml', 'r') as f:
                data = yaml.load(f)
            return data
        except FileNotFoundError as e:
            print('Configuration not yet created!')
            time.sleep(2)
    return None


def notify(config : Dict[str, str], data : Dict[str, str]):
    if config['method'] == 'Email':
        load_dotenv()

        GMAIL_USER=os.getenv('GMAIL_USER')
        GMAIL_PW=os.getenv('GMAIL_PW')

        mailer = yagmail.SMTP(GMAIL_USER, GMAIL_PW)

        # Formatting message
        config['message'] = config['message'].replace('$NOME',data['nome'])

        mailer.send(
            to=data['email'],
            subject='Aviso do sistema ConEg',
            contents=[yagmail.inline("./assets/coneg_icon.png"),'\n\n',config['message']]
            #yagmail.inline()
        )
    elif config['method'] == 'Telefone':
        pass
    else:
        print('This was an unnexpected behavior... 😵🥴')


def ins_clean_request(location : str, ts : str):
    """
    Inserts into fact table a request in which person was using
    mask. Hence this, we don't receive a frame of it.

    Args:
        location (str): Location configured on Inspector.
        ts (str): Timestamp using date and time (no time zone).
    """
    db = PsqlPy()
    # Status 0 -> wearing mask
    db.insert_row(
        local=location,
        ts=ts,
        status=0
    )           
    db.disconnect()