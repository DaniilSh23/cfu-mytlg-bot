FROM python:3.10-slim

RUN mkdir /mytlg_bot

COPY requirements.txt /mytlg_bot/

RUN python -m pip install -r /mytlg_bot/requirements.txt

COPY . /mytlg_bot/

WORKDIR /mytlg_bot

RUN ["python", "bot_authorization.py"]

ENTRYPOINT ["python", "main.py"]
