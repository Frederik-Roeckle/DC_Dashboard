
FROM python:3.11-alpine


WORKDIR /src


COPY ./requirements.txt /src/requirements.txt


RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY . /src


EXPOSE 8000


CMD ["python", "app.py"]