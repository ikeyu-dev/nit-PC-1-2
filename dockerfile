FROM python:3.12

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx || apt-get install -y libgl1

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./src /app/src

# 環境変数は.envまたはdocker-composeから設定される
ENV RASPI_API_URL=http://localhost:8000

EXPOSE 7001

CMD ["uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "7001"]