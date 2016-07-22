FROM python:2
MAINTAINER 3846masa <3846masahiro+git@gmail.com>

RUN mkdir /japont
COPY ./requirements.txt /japont/requirements.txt
RUN cd /japont && \
    pip install -r requirements.txt
COPY . /japont

VOLUME ["/japont/fonts"]
WORKDIR "/japont"

EXPOSE 8000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
