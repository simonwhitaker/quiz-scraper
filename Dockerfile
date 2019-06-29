FROM python:3.7.2
COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt
CMD [ "python", "quiz-scraper.py" ]
