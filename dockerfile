FROM python:3.9.5-buster

WORKDIR .

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN python fasttext_installer.py

EXPOSE 5000

ENTRYPOINT ["flask"]

CMD ["run", "--host=0.0.0.0"]
