FROM python:3.10-slim

#


WORKDIR /api_tg

#


COPY ./requirements.txt /api_tg/requirements.txt

#


RUN pip install --no-cache-dir --upgrade -r /api_tg/requirements.txt

#


COPY /app .




#

