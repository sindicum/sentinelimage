# 上位インポート先を追加
import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sentinelimage.sentinelimage import SentinelImage

# from sentinelimage import SentinelImage

# 画像取得したいポリゴン座標
coords = [[
    [143.29167898201092,43.248463884808274],
    [143.29104781830006,43.2455521734021],
    [143.2973895108188,43.244829697141114],
    [143.29799061911575,43.247719550773894],
    [143.29167898201092,43.248463884808274]
]]

# 出力画像名の接頭辞
image_name = 'usage'
# 対象期間（開始）
start_date ='2021-07-15'
# 対象期間（終了）
end_date = '2021-7-20'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 80
# GoogleDrive出力先フォルダ名
google_drive_dir = 'Download_From_GEE'
# EPSGコードの指定
crs = 'EPSG:3857'

# SentinelImageオブジェクトを作成（変数値の入力）
ee_obj = SentinelImage(coords, image_name, start_date, end_date,
                        cloudy_pixel_percentage_limit, google_drive_dir, crs)

# センチネル画像の撮影日（リストで取得）
shooting_date_list = ee_obj.shooting_date_list
print(shooting_date_list)

# 画像撮影日ごとに画像をGoogleDrive内に出力
for shooting_date in shooting_date_list:

    # センチネル画像取得（主要バンドB2,B3,B4,B8,B11,SCL）
    ee_obj.get_raw_image(shooting_date)

    # センチネル画像取得（トゥルーカラー）
    ee_obj.get_truecolor_image(shooting_date)
    
    # センチネル画像取得（NDVI）
    ee_obj.get_ndvi_image(shooting_date)
    
    # センチネル画像取得（EVI2）
    ee_obj.get_evi2_image(shooting_date)
    
    # センチネル画像取得（NDWI）
    ee_obj.get_ndwi_image(shooting_date)

    # 雲及び雲影をマスク処理したセンチネル画像の取得
    ee_obj.get_image_add_cldmask(shooting_date)
