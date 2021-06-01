FROM python:3.8
WORKDIR /coneg_inspetint
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN rm requirements.txt
COPY insp_coneg.py db_transactions.py ./
CMD ["python", "insp_coneg.py"]