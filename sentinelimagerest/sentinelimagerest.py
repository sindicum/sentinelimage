from __future__ import annotations
import json, os, urllib, requests
from re import A
from typing import Literal

import ee
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

import geopandas as gpd
import pandas as pd
from pyproj import Transformer, Geod
from rasterio.io import MemoryFile
from shapely.geometry import Polygon

'''
リクエストサイズが大きいと以下のエラーが発生
"Total request size must be less than or equal to 50331648 bytes.",
'''

SERVICE_ACCOUNT = os.environ.get('GCP_SERVICE_ACCOUNT')
KEY =  os.getcwd() + '/' + str(os.environ.get('GCP_KEY_FILE'))
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
PBULIC_PROJECT = 'projects/earthengine-public'
ASSETS = 'COPERNICUS/S2_SR_HARMONIZED'
ee_creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
ee.Initialize(ee_creds)

class SentinelImageREST:

    def __init__(self,
                    coords: list[list[list[float]]],
                    start_date: str,
                    end_date: str,
                    cloudy_pixel_percentage_limit: int,
                    output_image_dir: str,
                    field_name: str
                ):
        self.coords = coords
        self.field_name = field_name
        self.start_date = start_date
        self.end_date = end_date
        self.cloudy_pixel_percentage_limit = cloudy_pixel_percentage_limit
        self.output_image_dir = output_image_dir
        self.session = self.__create_session()
        
    def __create_session(self):
        credentials = service_account.Credentials.from_service_account_file(KEY)
        session = AuthorizedSession(credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform']))
        return session

    # 対象圃場の衛星データ撮影日をリストで取得
    def get_shootingdate_list(self) -> list[str]:
        parent = '{}/assets/{}'.format(PBULIC_PROJECT, ASSETS)
        url = 'https://earthengine.googleapis.com/v1/{}:listAssets?{}'.format(
        parent, urllib.parse.urlencode({
            "filter": "startTime >\"" + self.start_date + "T00:00:00+00:00\"\
                        AND endTime <\"" + self.end_date + "T23:59:59+00:00\"\
                        AND intersects(\"{'type':'Polygon', 'coordinates':" + str(self.coords) + "}\")\
                        AND properties.CLOUDY_PIXEL_PERCENTAGE <"  + str(self.cloudy_pixel_percentage_limit) ,
        }))

        response = self.session.get(url)
        content = response.content
        dict_data = json.loads(content)
        
        shooting_date_list = []
        if len(dict_data) == 0:
            return []
        else:
            for i in dict_data['assets']:
                shooting_date_list.append(i['startTime'][0:10])
            shooting_date_list = list(set(shooting_date_list))
            shooting_date_list.sort()
            return shooting_date_list

    # 5バンド（'B2','B3','B4','B8','B11'）のGeotiffファイルを取得、バッファー初期値は0
    def get_geotiff_raw(self,buffer: int=0):
                
        shooting_date_list = self.get_shootingdate_list()
        
        list_len = len(shooting_date_list)
        count = 0
        
        for shooting_date in shooting_date_list:
            
            count += 1
            print('download Raw GeoTIFF...',count,'/',list_len)
            
            try:
                image_content = self.__get_raw_image_content(self.coords,shooting_date,buffer)
            except requests.exceptions.ReadTimeout as e:
                print(e)
                print('ReCreate Session...')
                self.session = self.__create_session()
                image_content = self.__get_raw_image_content(self.coords,shooting_date,buffer)
            finally:
                # image_content取得エラー処理（GeoTIFFの先頭2バイトで判別を試みてる...）
                if image_content.hex()[:4] == '4d4d':
                    with open(self.output_image_dir + self.field_name +\
                                '_raw_' + shooting_date + '.tif','wb') as f:
                        f.write(image_content)
                else:
                    with open(self.output_image_dir + 'error_'+ self.field_name +\
                                '_raw_' + shooting_date + '.txt','wb') as f:
                        f.write(image_content)

    # 指定したVIのGeotiffファイルを取得、バッファー初期値は0
    def get_geotiff_vi(self,vi_name: Literal['NDVI','EVI2','NDWI'], buffer: int=0):
                
        shooting_date_list = self.get_shootingdate_list()

        list_len = len(shooting_date_list)
        count = 0

        for shooting_date in shooting_date_list:
            
            count += 1
            print('download ' + vi_name +' GeoTIFF...',count,'/',list_len)
            
            try:
                image_content = self.__get_vi_image_content(self.coords,shooting_date,vi_name,buffer)
            except requests.exceptions.ReadTimeout as e:
                print(e)
                print('ReCreate Session...')
                self.session = self.__create_session()
                image_content = self.__get_vi_image_content(self.coords,shooting_date,vi_name,buffer)
            finally:
                # image_content取得エラー処理（GeoTIFFの先頭2バイトで判別を試みてる...）
                if image_content.hex()[:4] == '4d4d':
                    with open(self.output_image_dir + self.field_name +\
                                '_' + vi_name + '_' + shooting_date + '.tif','wb') as f:
                        f.write(image_content)
                else:
                    with open(self.output_image_dir + 'error_'+ self.field_name +\
                                '_' + vi_name + '_' + shooting_date + '.txt','wb') as f:
                        f.write(image_content)


    # TrueColorのGeotiffファイルを取得、バッファー初期値は0
    def get_geotiff_tc(self, buffer: int=0):
                
        shooting_date_list = self.get_shootingdate_list()
        
        list_len = len(shooting_date_list)
        count = 0

        for shooting_date in shooting_date_list:
            
            count += 1
            print('download TrueColor GeoTIFF...',count,'/',list_len)
            
            try:
                image_content = self.__get_tc_image_content(self.coords,shooting_date,buffer)
            except requests.exceptions.ReadTimeout as e:
                print(e)
                print('ReCreate Session...')
                self.session = self.__create_session()
                image_content = self.__get_tc_image_content(self.coords,shooting_date,buffer)
            finally:
                # image_content取得エラー処理（GeoTIFFの先頭2バイトで判別を試みてる...）
                if image_content.hex()[:4] == '4d4d':
                    with open(self.output_image_dir + self.field_name +\
                                '_tc_' + shooting_date + '.tif','wb') as f:
                        f.write(image_content)
                else:
                    with open(self.output_image_dir + 'error_'+ self.field_name +\
                                '_tc_' + shooting_date + '.txt','wb') as f:
                        f.write(image_content)

    # GeoTIFFデータ（指定5バンド）の取得
    def __get_raw_image_content(self,coords, shooting_date: str, buffer: int=0):

        # バッファー0はエラーが出る
        if buffer == 0:
            clip_geom = ee.Geometry.Polygon(coords)
        else:
            clip_geom = ee.Geometry.Polygon(coords).buffer(buffer)

        def create_ee_image_object(shooting_date):
            ee_image_obj = ee.ImageCollection(ASSETS)\
                .filterBounds(ee.Geometry.Polygon(coords))\
                .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
                .select(['B2','B3','B4','B8','B11'])\
                .mean()\
                .reproject('EPSG:3857',None,10)\
                .clip(clip_geom)

            return ee_image_obj
        
        url = 'https://earthengine.googleapis.com/v1/projects/{}/image:computePixels'
        url = url.format(PROJECT_ID)
        response = self.session.post(
            url=url,
            data=json.dumps({
            'expression': ee.serializer.encode(create_ee_image_object(shooting_date)),
            'fileFormat': 'GEO_TIFF',
            'grid': {
                'crsCode': 'EPSG:3857'
                },
            })
        )
        return response.content

    # GeoTIFFデータ（指定VI）の取得
    def __get_vi_image_content(self,coords, shooting_date: str, vi_name: Literal['NDVI','EVI2','NDWI'], buffer: int=0):
        
        # バッファー0はエラーが出る
        if buffer == 0:
            clip_geom = ee.Geometry.Polygon(coords)
        else:
            clip_geom = ee.Geometry.Polygon(coords).buffer(buffer)
            
        def create_ee_image_object(shooting_date, vi_name):
            ee_image_obj = ee.ImageCollection(ASSETS)\
                .filterBounds(ee.Geometry.Polygon(coords))\
                .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
                .select(['B4','B8','B11'])\
                .mean()\
                .reproject('EPSG:3857',None,10)\
                .clip(clip_geom)
            
            if vi_name == 'NDVI':
                ee_image_obj = ee_image_obj\
                                .expression( '(nir - red) / (nir + red)',
                                            { 'nir':ee_image_obj.select('B8'),
                                                'red':ee_image_obj.select('B4') })\
                                .rename('NDVI')
            elif vi_name == 'EVI2':
                ee_image_obj = ee_image_obj\
                                .expression( '2.5 * (nir - red) / (nir + 2.4 * red + 10000)',
                                            { 'nir':ee_image_obj.select('B8'),
                                                'red':ee_image_obj.select('B4') })\
                                .rename('EVI2')
            elif vi_name == 'NDWI':
                ee_image_obj = ee_image_obj\
                                .normalizedDifference(['B4', 'B11'])\
                                .rename('NDWI')
            return ee_image_obj
        
        url = 'https://earthengine.googleapis.com/v1/projects/{}/image:computePixels'
        url = url.format(PROJECT_ID)
        response = self.session.post(
            url=url,
            data=json.dumps({
            'expression': ee.serializer.encode(create_ee_image_object(shooting_date,vi_name)),
            'fileFormat': 'GEO_TIFF',
            'grid': {
                'crsCode': 'EPSG:3857'
                },
            'bandIds': [vi_name],
            })
        )
        return response.content


    # GeoTIFFデータ（トゥルーカラー）の取得
    def __get_tc_image_content(self,coords, shooting_date: str, buffer: int=0):

        # バッファー0はエラーが出る
        if buffer == 0:
            clip_geom = ee.Geometry.Polygon(coords)
        else:
            clip_geom = ee.Geometry.Polygon(coords).buffer(buffer)
        
        def create_ee_image_object(shooting_date):
            ee_image_obj = ee.ImageCollection(ASSETS)\
                .filterBounds(ee.Geometry.Polygon(coords))\
                .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
                .select(['TCI_R', 'TCI_G', 'TCI_B'])\
                .mean()\
                .reproject('EPSG:3857',None,10)\
                .clip(clip_geom)

            return ee_image_obj
        
        url = 'https://earthengine.googleapis.com/v1/projects/{}/image:computePixels'
        url = url.format(PROJECT_ID)
        response = self.session.post(
            url=url,
            data=json.dumps({
            'expression': ee.serializer.encode(create_ee_image_object(shooting_date)),
            'fileFormat': 'GEO_TIFF',
            'grid': {
                'crsCode': 'EPSG:3857'
                },
            })
        )
        return response.content

    # 対象圃場の衛星データのAssetID（例：COPERNICUS/S2_SR/20210711T012659_20210711T013301_T54TXN）をリストで取得
    def get_asset_id_list(self) -> list[str]:

        parent = '{}/assets/{}'.format(PBULIC_PROJECT, ASSETS)
        url = 'https://earthengine.googleapis.com/v1/{}:listAssets?{}'.format(
        parent, urllib.parse.urlencode({
            "filter": "startTime >\"" + self.start_date + "T00:00:00+00:00\"\
                        AND endTime <\"" + self.end_date + "T23:59:59+00:00\"\
                        AND intersects(\"{'type':'Polygon', 'coordinates':" + str(self.coords) + "}\")\
                        AND properties.CLOUDY_PIXEL_PERCENTAGE <"  + str(self.cloudy_pixel_percentage_limit) ,
        }))

        response = self.session.get(url)
        content = response.content
        dict_data = json.loads(content)
        
        asset_id_list = []
        if len(dict_data) == 0:
            return []
        else:
            for i in dict_data['assets']:
                asset_id_list.append(i['id'])
            return asset_id_list

    # Geotiffファイル（各バンド）の取得
    def get_geotiff_raw_from_assetid(self, output_image_dir: str) -> None:
    
        asset_id_list = self.get_asset_id_list()

        list_len = len(asset_id_list)
        count = 0

        for asset_id in asset_id_list:

            count += 1
            print('download asset_ID GeoTIFF...',count,'/',list_len)
        
            name = '{}/assets/{}'.format(PBULIC_PROJECT, asset_id)
            url = 'https://earthengine.googleapis.com/v1/{}:getPixels'.format(name)
            body = json.dumps({
                'fileFormat': 'GEO_TIFF',
                'bandIds': ['B2', 'B3', 'B4', 'B8', 'B11'],
                'region': {"type":"Polygon", "coordinates": self.coords },
                'grid': {'crsCode': 'EPSG:3857'},
            })
        
            response = self.session.post(url, body)
            content = response.content
        
            asset_id_date = asset_id.split('/')[-1]
        
            with open(output_image_dir + self.field_name +\
                        '_raw_' + asset_id_date + '.tif','wb') as f:
                f.write(content)

    def create_vi_meshpolygon(self, coords: list[list[list[float]]],vi_name: Literal['NDVI','EVI2','NDWI'], 
                                shooting_date_list: list[str],buffer: int=0):

        # メッシュポリゴン格納用のGeoPandasオブジェクト
        meshpolygon = gpd.GeoDataFrame()
        # VIデータ格納用のPandasオブジェクト
        vi_data_stack = pd.DataFrame()
        
        for idx,shooting_date in enumerate(shooting_date_list):

            image_content = self.__get_vi_image_content(coords,shooting_date,vi_name,buffer)
            
            with MemoryFile(image_content) as memfile:
                with memfile.open() as rasterio_dataset:
                    
                    # for文初回時はメッシュポリゴンを生成
                    if idx == 0:
                        meshpolygon = self.__convert_rasterio_to_meshpolygon(rasterio_dataset)
                                            
                    # VIデータを読み込み
                    df = pd.DataFrame(rasterio_dataset.read()[0])
                    # 左上を起点にリスト化されたデータを縦一列に展開
                    df_stack = df.stack()
                    vi_data_stack[shooting_date] = df_stack.reset_index()\
                                                    .drop(['level_0','level_1'],axis=1)
            del memfile
        
        vi_data_stack['index'] = vi_data_stack.reset_index().index

        # メッシュポリゴンにVIデータをindexで結合
        merged_meshpolygon = meshpolygon.merge(vi_data_stack, on='index')
        merged_meshpolygon = merged_meshpolygon.drop('index', axis=1)
        # 圃場形状ポリゴンの作成（切り抜き用）
        mask_polygon = gpd.GeoDataFrame()
        mask_polygon.loc[0,'geometry'] = Polygon(coords[0])
        mask_polygon = mask_polygon.set_crs('epsg:4326')
        
        # 圃場形状ポリゴンに沿ってVIデータ入りメッシュポリゴンを切り抜き
        merged_meshpolygon = gpd.clip(gdf=merged_meshpolygon, mask=mask_polygon)
        return merged_meshpolygon
    
    # rasterio生データからメッシュポリゴンを作成
    @staticmethod
    def __convert_rasterio_to_meshpolygon(rasterio_dataset):
                
        dataset_width = rasterio_dataset.width
        dataset_height = rasterio_dataset.height

        # 入力座標参照系（NDVIラスタデータ）
        INPUT_CRS = "EPSG:3857"
        # 出力座標参照系（表示させたいベクタデータ）
        OUTPUT_CRS = "EPSG:4326"

        # 座標変換
        tf = Transformer.from_crs(INPUT_CRS, OUTPUT_CRS, always_xy=True)

        # NDVIファイルの左上・右上・左下・右下座標をそれぞれ取得（経度・緯度リスト）
        left_top = tf.transform(rasterio_dataset.bounds.left  , rasterio_dataset.bounds.top )
        right_top = tf.transform(rasterio_dataset.bounds.right , rasterio_dataset.bounds.top )
        left_bottom = tf.transform(rasterio_dataset.bounds.left  , rasterio_dataset.bounds.bottom )
        right_bottom = tf.transform(rasterio_dataset.bounds.right , rasterio_dataset.bounds.bottom )

        # 地点間を取り扱うGeodオブジェクトを準拠楕円体GRS80にて生成
        geod :Geod = Geod(ellps='GRS80')

        # NDVIファイル北端・西端ピクセル間の座標を取得（縦方向）
        # 引数は分かりにくいので公式ドキュメント参照のこと（https://pyproj4.github.io/pyproj/stable/api/geod.html）
        top_point_set   = geod.inv_intermediate(left_top[0], left_top[1], right_top[0],
                                                    right_top[1]  , dataset_width  + 1, 0 ,0 ,0)
        left_point_set  = geod.inv_intermediate(left_top[0], left_top[1], left_bottom[0],
                                                    left_bottom[1], dataset_height + 1, 0 ,0 ,0)
        y = left_point_set.lats
        x = top_point_set.lons
        
        # 空のGoeDataFrameオブジェクトを作成
        gpd_mesh_geometry = gpd.GeoDataFrame()
        gpd_mesh_geometry['geometry'] = None
        gpd_mesh_geometry = gpd_mesh_geometry.set_crs('epsg:4326')
        
        count = 0
        for y_index, y_value in enumerate(y[:-1]):
            for x_index, x_value in enumerate(x[:-1]):
                pixel_coordinates_list = [
                                            (x[x_index]       , y[y_index]      ),
                                            (x[x_index + 1]   , y[y_index]      ),
                                            (x[x_index + 1]   , y[y_index + 1]  ),
                                            (x[x_index]       , y[y_index + 1]  ),
                                        ]
                gpd_mesh_geometry.loc[count,'geometry'] = Polygon(pixel_coordinates_list)
                count += 1

        gpd_mesh_geometry['index'] = gpd_mesh_geometry.reset_index().index
        return gpd_mesh_geometry
    
    @staticmethod
    def convert_coords_list_to_tuple(coords: list[list[list[float]]]) -> list[list[tuple[float]]]:
        list_to_tuple = lambda x : tuple(x)
        return [list(map(list_to_tuple,coords[0]))]

    @staticmethod
    def convert_coords_tuple_to_list(coords: list[list[tuple[float]]]) -> list[list[list[float]]]:
        tuple_to_list = lambda x : list(x)
        return [list(map(tuple_to_list,coords[0]))]

    @staticmethod
    def transfomBoundingboxCRS(rasterioDataset, beforeEpsg, afterEpsg):
        west  = rasterioDataset.bounds.left
        south = rasterioDataset.bounds.bottom
        east  = rasterioDataset.bounds.right
        north = rasterioDataset.bounds.top
        trans_proj = Transformer.from_crs(beforeEpsg, afterEpsg, always_xy=True)
        nw4326 = trans_proj.transform(west, north)
        ne4326 = trans_proj.transform(east, north)
        se4326 = trans_proj.transform(east, south)
        sw4326 = trans_proj.transform(west, south)

        return [list(nw4326),list(ne4326),list(se4326),list(sw4326)]

    # foliumで表示されるためにnumpy形式の画像データとbounds（画像矩形座標）を取得
    def get_ndvi_for_folium(self, shooting_date: str, buffer: int=0):
        
        # バッファー0はエラーが出る
        if buffer == 0:
            clip_geom = ee.Geometry.Polygon(self.coords)
        else:
            clip_geom = ee.Geometry.Polygon(self.coords).buffer(buffer)
            

        ee_image_obj = ee.ImageCollection(ASSETS)\
            .filterBounds(ee.Geometry.Polygon(self.coords))\
            .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
            .select(['B8','B4'])\
            .mean()\
            .normalizedDifference(['B8', 'B4']).rename('NDVI')\
            .reproject('EPSG:3857',None,10)\
            .clip(clip_geom)

        url = 'https://earthengine.googleapis.com/v1/projects/{}/image:computePixels'
        url = url.format(PROJECT_ID)
        response = self.session.post(
            url=url,
            data=json.dumps({
            'expression': ee.serializer.encode(ee_image_obj),
            'fileFormat': 'GEO_TIFF',
            'grid': {
                'crsCode': 'EPSG:3857'
                },
            'bandIds': ['NDVI'],
            }),
        )
        image_content = response.content

        with MemoryFile(image_content) as memfile:
            with memfile.open() as rasterio_dataset:

                west  = rasterio_dataset.bounds.left
                south = rasterio_dataset.bounds.bottom
                east  = rasterio_dataset.bounds.right
                north = rasterio_dataset.bounds.top
                
                trans_proj = Transformer.from_crs('EPSG:3857',"EPSG:4326", always_xy=True)

                ne4326 = trans_proj.transform(east, north)
                sw4326 = trans_proj.transform(west, south)

                return {'image': rasterio_dataset.read()[0],'bounds':[[sw4326[1],sw4326[0]],[ne4326[1],ne4326[0]]]}
