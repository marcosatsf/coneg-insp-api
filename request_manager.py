from concurrent.futures import ThreadPoolExecutor
from db_transactions import PsqlPy
import face_recognition
import numpy as np
from glob import glob
import os


def multiprocess_recognition(
        location: str, 
        ts : str, 
        image_jpg : str
    ):
    """
    Tries to recognize a face and then register a new line
    into the fact table.

    Args:
        location (str): Location configured on Inspector.
        ts (str): Timestamp using date and time (no time zone).
        image_jpg (str): Filename including relative path to the
        image which we received on api request.
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(which_face, image_jpg)

        db = PsqlPy()
        # Returns the pesid from coneg.cadastros
        pesid = future.result()
        if pesid:
            # Status 2 -> not mask & registered
            db.insert_row(
                local=location,
                ts=ts,
                status=2,
                pessoa=pesid
            )
        else:
            # Status 1 -> not mask & not registered
            db.insert_row(
                local=location,
                ts=ts,
                status=1
            )           
        db.disconnect()
        # Remove temporary file received from inspector
        os.remove(image_jpg)


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