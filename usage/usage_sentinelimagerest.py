import glob,os,shutil,sys,unittest

# 上位インポート先を追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentinelimagerest.sentinelimagerest import SentinelImageREST



from sentinelimagerest import SentinelImageREST

# 画像取得したいポリゴン座標
coords =[[
    [143.276643,43.211713],
    [143.277662,43.211573],
    [143.277496,43.211322],
    [143.276525,43.211498],
    [143.276643,43.211713]
]]
# 対象期間（開始）
start_date ='2021-07-10'
# 対象期間（終了）
end_date = '2021-7-20'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 30
# 出力先フォルダ（相対パス）
output_dir = './'

field_name = 'usage'

# SentinelImageRESTクラスオブジェクトの作成
obj = SentinelImageREST(coords, start_date, end_date, cloudy_pixel_percentage_limit,output_dir,field_name)

# 対象圃場の衛星データ撮影日をリストで取得
print(obj.get_shootingdate_list())

# 5バンド（'B2','B3','B4','B8','B11'）のGeotiffファイルを取得、バッファー初期値は0
obj.get_geotiff_raw(-10)

# 指定したVIのGeotiffファイルを取得、バッファー初期値は0
obj.get_geotiff_vi('EVI2')

# TrueColorのGeotiffファイルを取得、バッファー初期値は0
obj.get_geotiff_tc()

# 対象圃場の衛星データのAssetID（例：COPERNICUS/S2_SR/20210711T012659_20210711T013301_T54TXN）をリストで取得
print(obj.get_asset_id_list())

# Geotiffファイル（各バンド）の取得
obj.get_geotiff_raw_from_assetid(output_dir)

# メッシュポリゴンに時系列VIデータを付与しGeoDataFrame形式で返す
obj.create_vi_meshpolygon('EVI2').to_file('test.fgb',index=False,driver='FlatGeobuf',spatial_index='No')

# foliumで表示されるためにnumpy形式のndviデータとbounds（画像矩形座標）を取得
print(obj.get_numpy_ndvi(obj.get_shootingdate_list()[0]))

# foliumで表示されるためにnumpy形式のtcデータとbounds（画像矩形座標）を取得
print(obj.get_numpy_tc(obj.get_shootingdate_list()[0]))
