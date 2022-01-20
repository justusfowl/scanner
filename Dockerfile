FROM python:3.8-slim-buster

COPY . /
RUN mkdir -p /mondir
RUN pip install -r /requirements.txt

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-deu ghostscript 

CMD [ "python", "./Scanner.py"]