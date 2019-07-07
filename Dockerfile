FROM python:3.7.2-alpine as build
COPY . /src
WORKDIR /src
RUN apk --no-cache --update add \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    musl-dev \
    openssl-dev \
    && \
    mkdir /usr/include/libxml && \
    ln -s /usr/include/libxml2/libxml/xmlversion.h /usr/include/xmlversion.h && \
    ln -s /usr/include/libxml2/libxml/xmlversion.h /usr/include/libxml/xmlversion.h && \
    ln -s /usr/include/libxml2/libxml/xmlexports.h /usr/include/xmlexports.h && \
    ln -s /usr/include/libxml2/libxml/xmlexports.h /usr/include/libxml/xmlexports.h && \
    pip --no-cache-dir install -r requirements.txt
CMD [ "python", "quiz-scraper.py" ]
