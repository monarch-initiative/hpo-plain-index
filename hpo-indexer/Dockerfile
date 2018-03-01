FROM python:3.6-alpine

ADD . /hpo-indexer
WORKDIR /hpo-indexer

RUN pip install -r requirements.txt

ENV PATH="/hpo-indexer/scripts/:/hpo-indexer/:$PATH"
