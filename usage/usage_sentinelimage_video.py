import glob,os,shutil,sys,unittest

# 上位インポート先を追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentinelimage.sentinelimage import SentinelImage

# 動画取得したいポリゴン座標
coords = [[
    [141.532745,42.983993],
    [141.532745,42.998056],
    [141.567507,42.998056],
    [141.567507,42.983993],
    [141.532745,42.983993]
]]

# 出力動画名の接頭辞
image_name = 'escon'
# 対象期間（開始）
start_date ='2019-04-15'
# 対象期間（終了）
end_date = '2022-10-30'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 25
# GoogleDrive出力先フォルダ名
google_drive_dir = 'Download_From_GEE'
# EPSGコードの指定
crs = 'EPSG:3857'
# 動画フレームレート（フレーム/秒）
framesPerSecond=2.5

# SentinelImageオブジェクトを作成（変数値の入力）
ee_obj = SentinelImage(coords, image_name, start_date, end_date,
                        cloudy_pixel_percentage_limit, google_drive_dir, crs)

# センチネル画像撮影日（リストで取得）
shooting_date_list = ee_obj.shooting_date_list
print(shooting_date_list)

# センチネル動画取得（トゥルーカラー）
ee_obj.get_truecolor_video(framesPerSecond)