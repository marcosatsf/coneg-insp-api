FROM python:3.8
WORKDIR /coneg_inspetint
RUN apt-get update -y && \
    apt-get install build-essential cmake pkg-config -y
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt
RUN mkdir tmp
COPY /sql ./sql/
COPY insp_coneg.py db_transactions.py request_manager.py ./
CMD ["python", "insp_coneg.py"]