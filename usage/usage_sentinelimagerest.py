# 上位インポート先を追加
import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sentinelimagerest.sentinelimagerest import SentinelImageREST

# from sentinelimagerest import SentinelImageREST

# 画像取得したいポリゴン座標
coords = [[
    [143.29167898201092,43.248463884808274],
    [143.29104781830006,43.2455521734021],
    [143.2973895108188,43.244829697141114],
    [143.29799061911575,43.247719550773894],
    [143.29167898201092,43.248463884808274]
]]

field_name = 'usage_rest'
# 対象期間（開始）
start_date ='2021-07-01'
# 対象期間（終了）
end_date = '2021-7-25'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 30
# 出力先フォルダ（相対パス）
output_dir = './'


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
asset_id_list = obj.get_asset_id_list()
print('asset_id_list',asset_id_list)

for asset_id in asset_id_list:
    obj.get_geotiff_raw_with_assetid(asset_id)


# メッシュポリゴンに時系列VIデータを付与しGeoDataFrameデータをFlatGeobuf形式で保存（Q-GIS3.16で動作確認）
obj.create_vi_meshpolygon('EVI2').to_file('test.fgb',index=False,driver='FlatGeobuf',spatial_index='No')

# メッシュポリゴンに時系列VIデータを付与しGeoDataFrameデータをShapeFile形式で保存（汎用性を求める場合）
obj.create_vi_meshpolygon('EVI2').to_file('test.shp')

# foliumで表示されるためにnumpy形式のndviデータとbounds（画像矩形座標）を取得
print(obj.get_numpy_ndvi(obj.get_shootingdate_list()[0]))

# foliumで表示されるためにnumpy形式のtcデータとbounds（画像矩形座標）を取得
print(obj.get_numpy_tc(obj.get_shootingdate_list()[0]))
