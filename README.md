## インストール
```
pip install git+https://github.com/sindicum/sentinelimage.git
```
依存ライブラリは、earthengine-api, geetools

## 使用法
- Google Earth Engine(GEE)へのアカウント登録（SignUp）を予め行う必要あり  
&emsp;https://developers.google.com/earth-engine
- GEEのREST APIを使用する場合はGoogle Cloud Platform（GCP）でサービスアカウントを発行する必要あり  
&emsp;https://developers.google.com/earth-engine/reference
- 非営利組織、研究科学者、その他非商用および研究プロジェクト、個人（非商用）の場合は無償利用が可能とのこと（詳細は利用規約参照）
- 使用方法はusageディレクトリを参照

## REST APIを使用時の設定
1.GCPでサービスアカウントを発行し鍵ファイルをプログラム実行階層に配置  
2.以下の環境変数を設定（Dockerを使う場合はdocker.envファイルに記述）  
```
GCP_KEY_FILE='<キーファイル名>.json'
GCP_PROJECT_ID='<プロジェクトID名>'
GCP_SERVICE_ACCOUNT='<サービスアカウント名>@<プロジェクトID名>.iam.gserviceaccount.com'
```
3.依存ライブラリ  
geopandas, pandas, pyproj, rasterio, shapely