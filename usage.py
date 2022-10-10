from typing import Union
from sentinelimage import SentinelImage

coords = [[
    [ 143.318056522214533, 43.242223343374064 ],
    [ 143.320506245670259, 43.241908424574177 ],
    [ 143.319809755668103, 43.239091578468283 ],
    [ 143.317624218075224, 43.239459000563237 ],
    [ 143.318056522214533, 43.242223343374064 ]
]]

image_name: str = 'usage'
start_date: str ='2021-07-10'
end_date: str = '2021-7-20'
cloudy_pixel_percentage_limit: int = 80
google_drive_dir: str = 'Download_From_GEE'

# SentinelImageオブジェクトを作成
ee_obj = SentinelImage(coords, image_name, start_date, end_date,
                        cloudy_pixel_percentage_limit, google_drive_dir)

# センチネル画像撮影日（リストで取得）
shooting_date_list = ee_obj.shooting_date_list
print(shooting_date_list)

for shooting_date in shooting_date_list:

    # センチネル画像取得（主要バンドB2,B3,B4,B8,B11,SCL）
    ee_obj.get_raw_image(shooting_date)

    # センチネル画像取得（トゥルーカラー）
    ee_obj.get_truecolor_image(shooting_date)
    
    # # センチネル画像取得（NDVI）
    ee_obj.get_ndvi_image(shooting_date)
    
    # # センチネル画像取得（EVI2）
    ee_obj.get_evi2_image(shooting_date)
    
    # センチネル画像取得（NDWI）
    ee_obj.get_ndwi_image(shooting_date)

    # マスク処理センチネル画像取得
    ee_obj.get_image_add_cldmasked(shooting_date)