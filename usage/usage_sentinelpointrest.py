from sentinelimagerest.sentinelpointrest import SentinelPointREST

# 画像取得したいポイント座標
point_coords = [143.276643,43.211713]

# 対象期間（開始）
start_date ='2021-07-10'
# 対象期間（終了）
end_date = '2021-7-20'
# 雲被覆率フィルタリングの上限値
cloudy_pixel_percentage_limit = 30

# SentinelPointRESTクラスオブジェクトの作成
obj = SentinelPointREST(point_coords, start_date, end_date, cloudy_pixel_percentage_limit)

# 対象圃場の衛星データ撮影日をリストで取得
shooting_date_list = obj.get_shootingdate_list()
print(shooting_date_list)

# 対象圃場の衛星データのAssetID（例：COPERNICUS/S2_SR/20210711T012659_20210711T013301_T54TXN）をリストで取得
assetid_list = obj.get_asset_id_list()
print(assetid_list)

# 各バンド反射率（0〜10000）を配列で取得
reflectance_array = obj.get_point_data_from_assetid(assetid_list[0])
print(reflectance_array)

# 各バンド反射率（0〜1）、NDVI、EVI2を辞書形式で取得
reflectance_dict = obj.get_computed_point_data()
print(reflectance_dict)

# 各バンド反射率（0〜1）、NDVI、EVI2をGeoPandasのGeoDataFrame形式で取得
reflectance_gdf = obj.get_point_gdf()
print(reflectance_gdf)