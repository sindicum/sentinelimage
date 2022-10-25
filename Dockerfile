FROM python:3.9

# 環境変数を設定
ENV PYTHONUNBUFFERED 1
# コンテナ内に/codeディレクトリを作成
RUN mkdir /code
# ワークディレクトリの設定
WORKDIR /code

#  クリーン状態ではfionaやRtreeがエラーを起こす。
RUN apt-get update && apt-get install -y \
    tzdata\
    libgdal-dev\
    libspatialindex-dev\
    gdal-bin\
    python3-rtree 

# pip自体のアップデートdo
RUN pip install --upgrade pip

# setuptools58で2to3サポートを廃止したことによるGDALインストールエラーの発生を回避
# https://setuptools.pypa.io/en/latest/history.html
# https://stackoverflow.com/questions/69123406/error-building-pygdal-unknown-distribution-option-use-2to3-fixers-and-use-2
RUN pip install setuptools==57.5.0

# GDAL依存関係から先にnumpyをインストール
RUN pip install numpy==1.22.2
# GDAL==3.4.1はインストールエラー発生
RUN pip install GDAL==3.2.3

# requirements.txtを/code/にコピーする
ADD requirements.txt /code/

# requirements.txtに基づきパッケージインストール
RUN pip install -r requirements.txt