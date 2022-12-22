import ee
# from google.auth.transport.requests import AuthorizedSession
# from google.oauth2 import service_account

# import geopandas as gpd
# import pandas as pd
# from pyproj import Transformer, Geod
# from rasterio.io import MemoryFile
# from shapely.geometry import Polygon
import os

SERVICE_ACCOUNT = os.environ.get('GCP_SERVICE_ACCOUNT')
KEY =  os.environ.get('GCP_KEY_FILE')
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
PBULIC_PROJECT = 'projects/earthengine-public'
ASSETS = 'COPERNICUS/S2_SR_HARMONIZED'
ee_creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
ee.Initialize(ee_creds)



# 画像取得したいポリゴン座標
coords = [[
    [ 143.318056522214533, 43.242223343374064 ],
    [ 143.320506245670259, 43.241908424574177 ],
    [ 143.319809755668103, 43.239091578468283 ],
    [ 143.317624218075224, 43.239459000563237 ],
    [ 143.318056522214533, 43.242223343374064 ]
]]

# 出力画像名の接頭辞
image_name = 'usage'
# 撮影日
shooting_date ='2021-07-16'

# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 80
# GoogleDrive出力先フォルダ名
google_drive_dir = 'Download_From_GEE'

crs = 'EPSG:6681'


image = ee.ImageCollection(ASSETS)\
        .filterBounds(ee.Geometry.Polygon(coords))\
        .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',cloudy_pixel_percentage_limit))\
        .select(['B2','B3','B4','B8','B11','SCL'])
        
task = ee.batch.Export.image.toDrive(
        image = image,
        region = ee.Geometry.Polygon(coords),
        folder = google_drive_dir,
        fileNamePrefix = 'playground',
        scale = 10,
        crs = crs,
        maxPixels = 100000000
        )

task.start()

# 画像は何処に行った？
# gcloudのインストールが必要？？