from __future__ import annotations
import json, io, os, urllib

import ee
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

import geopandas as gpd
import numpy
from shapely.geometry import Point


SERVICE_ACCOUNT = os.environ.get('GCP_SERVICE_ACCOUNT')
KEY =  os.environ.get('GCP_KEY_FILE')
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
PBULIC_PROJECT = 'projects/earthengine-public'
ASSETS = 'COPERNICUS/S2_SR_HARMONIZED'
ee_creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY)
ee.Initialize(ee_creds)

class SentinelPointREST:
        
    def __init__(self, point_coords: list[float], start_date: str, end_date: str,
                    cloudy_pixel_percentage_limit: int ):
        self.point_coords = point_coords
        self.start_date = start_date
        self.end_date = end_date
        self.cloudy_pixel_percentage_limit = cloudy_pixel_percentage_limit
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
                        AND intersects(\"{'type':'Point', 'coordinates':" + str(self.point_coords) + "}\")\
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

    # 対象圃場の衛星データのAssetID（例：COPERNICUS/S2_SR/20210711T012659_20210711T013301_T54TXN）をリストで取得
    def get_asset_id_list(self) -> list[str]:
        
        parent = '{}/assets/{}'.format(PBULIC_PROJECT, ASSETS)
        url = 'https://earthengine.googleapis.com/v1/{}:listAssets?{}'.format(
        parent, urllib.parse.urlencode({
            "filter": "startTime >\"" + self.start_date + "T00:00:00+00:00\"\
                        AND endTime <\"" + self.end_date + "T23:59:59+00:00\"\
                        AND intersects(\"{'type':'Point', 'coordinates':" + str(self.point_coords) + "}\")\
                        AND properties.CLOUDY_PIXEL_PERCENTAGE <"  + str(self.cloudy_pixel_percentage_limit) ,
        }))

        response = self.session.get(url)
        content = response.content
        dict_data = json.loads(content)
        print(dict_data)
        asset_id_list = []
        if len(dict_data) == 0:
            return []
        else:
            for i in dict_data['assets']:
                asset_id_list.append(i['id'])
            return asset_id_list

    # 各バンド反射率（0〜10000）を配列で取得
    def get_point_data_from_assetid(self, asset_id: str) -> tuple[int, int, int, int, int]:
        name = '{}/assets/{}'.format(PBULIC_PROJECT, asset_id)
        url = 'https://earthengine.googleapis.com/v1/{}:getPixels'.format(name)

        body = json.dumps({
            'fileFormat': 'NPY',
            'bandIds': ['B2', 'B3', 'B4', 'B8', 'B11'],
            'region': {"type":"Point", "coordinates": self.point_coords },
        })
        pixels_response = self.session.post(url, body)
        pixels_content = pixels_response.content
        array = numpy.load(io.BytesIO(pixels_content))
        # arrayの例 [[(1518, 2094, 1399, 7784, 3990)]]
        return array[0][0]

    # 各バンド反射率（0〜1）、NDVI、EVI2を辞書形式で取得
    def get_computed_point_data(self):

        def create_ee_image_object(shooting_date):
            ee_image_obj = ee.ImageCollection(ASSETS)\
                .filterBounds(ee.Geometry.Point(self.point_coords))\
                .filterDate(ee.Date(shooting_date), ee.Date(shooting_date).advance(1,'day'))\
                .select(['B2','B3','B4','B8','B11'])\
                .mean()\
                .reproject('EPSG:4326',None,10)\
                .clip(ee.Geometry.Point(self.point_coords))
            return ee_image_obj
        
        shooting_date_list = self.get_shootingdate_list()
        point_raw_array = []
        
        for shooting_date in shooting_date_list:
            url = 'https://earthengine.googleapis.com/v1/projects/{}/image:computePixels'
            url = url.format(PROJECT_ID)
            response = self.session.post(
                url=url,
                data=json.dumps({
                'expression': ee.serializer.encode(create_ee_image_object(shooting_date)),
                'fileFormat': 'NPY',
                })
            )
            pixel_content = response.content
            array = numpy.load(io.BytesIO(pixel_content))

            b2 = float('{:.4f}'.format(array[0][0][0]/10000)) 
            b3 = float('{:.4f}'.format(array[0][0][1]/10000)) 
            b4 = float('{:.4f}'.format(array[0][0][2]/10000)) 
            b8 = float('{:.4f}'.format(array[0][0][3]/10000)) 
            b11 = float('{:.4f}'.format(array[0][0][4]/10000)) 
            ndvi = float('{:.4f}'.format((b8-b4)/(b8+b4)))
            evi2 = float('{:.4f}'.format(2.5*(b8-b4)/(b8+2.4*b4+1))) 

            point_raw_array.append({
                'shooting_date':str(shooting_date),
                'data':{'B2':b2,'B3':b3,'B4':b4,'B8':b8,'B11':b11,'ndvi':ndvi,'evi2':evi2 }
                })
        return point_raw_array
    
    # 各バンド反射率（0〜1）、NDVI、EVI2をGeoPandasのGeoDataFrame形式で取得
    def get_point_gdf(self):
        
        gdf = gpd.GeoDataFrame()
        gdf['geometry'] = None
        gdf = gdf.set_crs('epsg:4326')
        
        point_data_list = self.get_computed_point_data()
        for idx,point_data in enumerate(point_data_list):
            
            lng = self.point_coords[0]
            lat = self.point_coords[1]
            shooting_date = point_data['shooting_date']
            b2 =  point_data['data']['B2']
            b3 =  point_data['data']['B3']
            b4 =  point_data['data']['B4']
            b8 =  point_data['data']['B8']
            b11 =  point_data['data']['B11']
            ndvi = point_data['data']['ndvi']
            evi2 = point_data['data']['evi2']
            
            gdf.loc[idx,'geometry'] = Point(lng,lat)
            gdf.loc[idx,'shooting_date'] = shooting_date
            gdf.loc[idx,'B2'] = b2
            gdf.loc[idx,'B3'] = b3
            gdf.loc[idx,'B4'] = b4
            gdf.loc[idx,'B8'] = b8
            gdf.loc[idx,'B11'] = b11
            gdf.loc[idx,'NDVI'] = ndvi
            gdf.loc[idx,'EVI2'] = evi2
        
        return gdf
    
