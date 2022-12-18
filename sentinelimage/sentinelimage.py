# バッチダウンロードのためgeetoolsをインポート
from geetools import batch
import ee

# ブラウザ経由で認証
ee.Authenticate()
ee.Initialize()

class SentinelImage():
    
    data_set = "COPERNICUS/S2_SR_HARMONIZED"
    
    def __init__(self,
                    coords,
                    image_name,
                    start_date,
                    end_date,
                    cloudy_pixel_percentage_limit,
                    google_drive_dir,
                    crs
                ):
        self.ee = ee
        self.coords = coords
        self.image_name = image_name
        self.start_date = start_date
        self.end_date = end_date
        self.cloudy_pixel_percentage_limit = cloudy_pixel_percentage_limit
        self.google_drive_dir = google_drive_dir
        self.crs = crs
        self.shooting_date_list = self.__getShootingDate()
    
    # センチネル画像取得（主要バンドB2,B3,B4,B8,B11,SCL）
    def get_raw_image(self,shooting_date):

        img=self.__imageCollection_S2SR_Raw(shooting_date).mean()
        fileNamePrefix = shooting_date + '_RAW'
        self.__downloadImageToDrive(img,fileNamePrefix)
    
    # センチネル画像取得（トゥルーカラー）
    def get_truecolor_image(self,shooting_date):

        img=self.__imageCollection_S2SR_TC(shooting_date).mean()
        fileNamePrefix = shooting_date + '_TC'
        self.__downloadImageToDrive(img,fileNamePrefix)

    # センチネル画像取得（NDVI）
    def get_ndvi_image(self,shooting_date):

        img =self.__imageCollection_S2SR_Raw(shooting_date).mean()
        img_ndvi = img.expression(
                        '(nir - red) / (nir + red)',
                        { 'nir':img.select('B8'), 'red':img.select('B4')}
                    ).rename('ndvi')
        fileNamePrefix = shooting_date + '_NDVI'
        self.__downloadImageToDrive(img_ndvi,fileNamePrefix)
    
    # センチネル画像取得（EVI2）
    def get_evi2_image(self,shooting_date):
        
        img =self.__imageCollection_S2SR_Raw(shooting_date).mean()
        # バンド反射率整数値の式（小数値の反射率であれば'2.5 * (nir - red) / (nir + 2.4 * red + 1)'で示される）
        # evi2_expression = '2.5 * (nir - red) / (nir + 2.4 * red + 10000)'
        img_evi2 = img.expression(
                        '2.5 * (nir - red) / (nir + 2.4 * red + 10000)',
                        { 'nir':img.select('B8'), 'red':img.select('B4')}
                    ).rename('evi2')
        fileNamePrefix = shooting_date + '_EVI2'
        self.__downloadImageToDrive(img_evi2,fileNamePrefix)

    # センチネル画像取得（NDWI）
    def get_ndwi_image(self,shooting_date):

        img =self.__imageCollection_S2SR_Raw(shooting_date).mean()
        img_ndwi= img.normalizedDifference(['B4','B11']).rename('ndwi')
        fileNamePrefix = shooting_date + '_NDWI'
        self.__downloadImageToDrive(img_ndwi,fileNamePrefix)
    
    # センチネル画像撮影日（リストで取得）
    def __getShootingDate(self):
        imgCollection = (self.ee.ImageCollection(self.data_set)
                        .filterBounds(self.ee.Geometry.Polygon(self.coords))
                        .filterDate(self.start_date, self.end_date)
                        .filter(self.ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',self.cloudy_pixel_percentage_limit)))

        # 取得した画像の撮影日をリストで取得（distinctで重複を排除）
        filteredImgList =  (self.ee.List(imgCollection.aggregate_array('system:time_start'))
                            .map(lambda d : self.ee.Date(d).format('YYYY-MM-dd'))
                            .distinct()
                            )
        # 撮影日リストの取得
        return filteredImgList.getInfo()
    
    # Sentinel2イメージコレクションの生成（衛星、日にち、対象地域、バンド）
    def __imageCollection_S2SR_Raw(self,shooting_date):
        return self.ee.ImageCollection(self.data_set)\
                    .filterBounds(self.ee.Geometry.Polygon(self.coords))\
                    .filterDate(self.ee.Date(shooting_date), self.ee.Date(shooting_date).advance(1,'day'))\
                    .filter(self.ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',self.cloudy_pixel_percentage_limit))\
                    .select(['B2','B3','B4','B8','B11','SCL'])

    def __imageCollection_S2SR_TC(self,shooting_date):
        return self.ee.ImageCollection(self.data_set)\
                    .filterBounds(self.ee.Geometry.Polygon(self.coords))\
                    .filterDate(self.ee.Date(shooting_date), self.ee.Date(shooting_date).advance(1,'day'))\
                    .filter(self.ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',self.cloudy_pixel_percentage_limit))\
                    .select(['TCI_R','TCI_G','TCI_B'])
        
    # イメージをGoogleDriveに保存（maxPixelsはデフォルト1億ピクセルから10億ピクセルに変更）
    def __downloadImageToDrive(self, image, fileNamePrefix):
        task = self.ee.batch.Export.image.toDrive(
                image = image,
                region = self.ee.Geometry.Polygon(self.coords),
                folder = self.google_drive_dir,
                fileNamePrefix = self.image_name + '_' + self.crs + '_' + fileNamePrefix,
                scale = 10,
                crs = self.crs,
                maxPixels = 1000000000
                )
        task.start()
        
    # イメージコレクションをGoogleDriveに保存
    def __downloadImageCollectionToDrive(self, imageCollection, fileNamePrefix):
                
        batch.Export.imagecollection.toDrive(
            collection=imageCollection,
            folder=self.google_drive_dir,
            namePattern= self.image_name + '_' + self.crs + '_' + fileNamePrefix +  '_{id}',
            scale= 10,
            region= self.ee.Geometry.Polygon(self.coords),
            crs= self.crs
            )

    def get_asset_id(self):
        
        imgCollection=self.ee.ImageCollection(self.data_set)\
                    .filterDate(self.start_date, self.end_date)\
                    .filterBounds(self.ee.Geometry.Polygon(self.coords))\

        return imgCollection.aggregate_array('system:index').getInfo()

    def get_spacecraft_name(self):
        
        imgCollection=self.ee.ImageCollection(self.data_set)\
                    .filterDate(self.start_date, self.end_date)\
                    .filterBounds(self.ee.Geometry.Polygon(self.coords))\

        return imgCollection.aggregate_array('SPACECRAFT_NAME').getInfo()

    def get_asset_id_image(self,asset_id):
        image=self.ee.Image(asset_id).select(['B2','B3','B4','B8','B11','SCL'])

        fileNamePrefix = 'asset_id'
        self.__downloadImageToDrive(image,fileNamePrefix)
        
    # バッチ処理の状態確認
    def task_status(self):
        tasks = self.ee.batch.Task.list()
        for j in tasks:
            print(j)
    
    # センチネル画像（主要バンドB2,B3,B4,B8,B11,SCL）にS2_CLOUD_PROBABILITYを合成し雲マスク処理
    # https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless
    def get_image_add_cldmask(self, SHOOTING_DATE, CLD_PRB_THRESH = 50, 
                                NIR_DRK_THRESH = 0.15, CLD_PRJ_DIST = 1, BUFFER = 50):
        
        # CLD_PRB_THRESH = 50(%)
        # NIR_DRK_THRESH = 0.15(100分率)
        # CLD_PRJ_DIST = 1(km),
        # BUFFER = 50(m)
        
        # S2_CLOUD_PROBABILITYを合成
        def get_sr2_cldprb_imgcol(shooting_date):

            s2_sr_col = (self.ee.ImageCollection(self.data_set)
                .filterBounds(self.ee.Geometry.Polygon(self.coords))
                .filterDate(self.ee.Date(shooting_date),self.ee.Date(shooting_date).advance(1,'day'))
                .filter(self.ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.cloudy_pixel_percentage_limit))
                .select(['B2','B3','B4','B8','B11','SCL',]))

            s2_cloudless_col = (self.ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
                .filterBounds(self.ee.Geometry.Polygon(self.coords))
                .filterDate(self.ee.Date(shooting_date),self.ee.Date(shooting_date).advance(1,'day')))

            s2_sr_cld_col_eval = self.ee.ImageCollection(self.ee.Join.saveFirst('s2cloudless').apply(**{
                    'primary': s2_sr_col,
                    'secondary': s2_cloudless_col,
                    'condition': ee.Filter.equals(**{
                        'leftField': 'system:index',
                        'rightField': 'system:index'
                    })
                }))
            
            return s2_sr_cld_col_eval.map(lambda img:img.addBands(self.ee.Image(img.get('s2cloudless')).rename('CLD_PRB')))

        # 雲および雲陰内ダークピクセルをマスク化
        def get_cloud_mask_img(img):
            
            clouds = img.select('CLD_PRB').gt(CLD_PRB_THRESH)

            transformed_cld_img = (clouds.directionalDistanceTransform(
                                            ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE'))),
                                            CLD_PRJ_DIST*10
                                            )
                                        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
                                        .select('distance')
                                        .mask()
                                        .rename('cloud_transform'))
            
            dark_pixels_img = img.select('B8').lt(NIR_DRK_THRESH*1e4).multiply(img.select('SCL').neq(6)).rename('dark_pixels')

            shadows = transformed_cld_img.multiply(dark_pixels_img).rename('shadows')

            is_cld_shdw = clouds.select('CLD_PRB').add(shadows.select('shadows')).gt(0)

            cloudmask =  (is_cld_shdw.focalMin(2).focalMax(BUFFER*2/20)
                .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
                .selfMask()
                .rename('CLD_MASK'))

            return img.addBands(cloudmask)
        
        # 撮影日のイメージコレクションを取得し各画像をマスク処理
        imgcol = get_sr2_cldprb_imgcol(SHOOTING_DATE)
        ctf_imgcol = imgcol.map(lambda img: get_cloud_mask_img(img))
        
        fileNamePrefix = SHOOTING_DATE + '_CLDMASK'
        # toUnint16()でキャストしておりnanはすべて0になる。
        self.__downloadImageToDrive(ctf_imgcol.mean().toUint16(),fileNamePrefix)
        