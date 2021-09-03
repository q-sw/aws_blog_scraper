FROM alpine:3.14.2

RUN apk add --no-cache python3 py-pip

RUN mkdir /opt/blog_scrapper
WORKDIR /opt/blog_scrapper

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache

COPY script.py /opt/blog_scrapper/
COPY config.json /opt/blog_scrapper/

CMD ["python3", "script.py"]