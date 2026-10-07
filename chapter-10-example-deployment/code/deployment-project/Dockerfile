FROM python:3.11-slim
WORKDIR /app
COPY ["model.bin", "predict.py", "requirements.txt", "./"]
RUN pip install -r requirements.txt
EXPOSE 9696
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:9696", "predict:app"]
