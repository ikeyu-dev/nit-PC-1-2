FROM python:3.12

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx || apt-get install -y libgl1

RUN pip install -r /requirements.txt

COPY ./src /src

CMD ["uvicorn", "src.api.main:app", "--reload",  "--host", "0.0.0.0", "--port", "7001"]