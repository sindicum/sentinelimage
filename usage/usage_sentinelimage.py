from sentinelimage import SentinelImage

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
# 対象期間（開始）
start_date ='2021-07-10'
# 対象期間（終了）
end_date = '2021-7-20'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 80
# GoogleDrive出力先フォルダ名
google_drive_dir = 'Download_From_GEE'

crs = 'EPSG:6681'

# SentinelImageオブジェクトを作成（変数値の入力）
ee_obj = SentinelImage(coords, image_name, start_date, end_date,
                        cloudy_pixel_percentage_limit, google_drive_dir, crs)

# センチネル画像撮影日（リストで取得）
shooting_date_list = ee_obj.shooting_date_list
print(shooting_date_list)

# 画像撮影日ごとに画像をGoogleDrive内に出力
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
    ee_obj.get_image_add_cldmask(shooting_date)
