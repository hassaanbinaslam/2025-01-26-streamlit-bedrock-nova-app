FROM public.ecr.aws/docker/library/python:3.12.1-slim

EXPOSE 8501

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]