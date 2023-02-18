# python:3.9-slim-bullseyeはビルドエラーが出るので不可
FROM python:3.9-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /workspace

RUN apt-get update && apt-get install -y\
    tzdata\
    libgdal-dev\
    libspatialindex-dev\
    gdal-bin\
    python3-rtree

RUN pip install --upgrade pip
RUN pip install setuptools==57.5.0
RUN pip install numpy==1.22.2
RUN pip install GDAL==3.2.3
COPY ./requirements.txt /workspace/
RUN pip install -r requirements.txt

# Jupyter Labでインタラクティブのウィジェットを使用する設定
RUN jupyter nbextension install --py widgetsnbextension --user
RUN jupyter nbextension enable widgetsnbextension --user --py