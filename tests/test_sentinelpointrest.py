import glob,os,shutil,sys,unittest

# 上位インポート先を追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sentinelimagerest.sentinelpointrest import SentinelPointREST

class TestSentinelPointREST(unittest.TestCase):

    def setUp(self):
        # test data
        self.point_coord_1 = [143.259809255420208, 43.205058676946557]
        self.point_coord_2 = [143.259069998301072, 43.204947020820448]
        self.point_coord_3 = [143.259209589966844, 43.204747100239807]
        
        self.start_date = '2021-07-16'
        self.end_date = '2021-07-21'
        self.cloudy_pixel_percentage_limit = 100
        
        self.obj1 = SentinelPointREST(self.point_coord_1, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit)
        self.obj2 = SentinelPointREST(self.point_coord_2, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit)
        self.obj3 = SentinelPointREST(self.point_coord_3, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit)
        
        self.asset_id = 'COPERNICUS/S2_SR_HARMONIZED/20210716T012701_20210716T012658_T54TXN'

        # GeoTIFF上での地点とPoint取得APIで値が微妙にずれる場合がある（要検証）
        self.b2_1 = {'from_asset_id':726,'from_computed_mean':0.0742,'from_image':742}
        self.b2_2 = {'from_asset_id':787,'from_computed_mean':0.0787,'from_image':774}
        self.b2_3 = {'from_asset_id':729,'from_computed_mean':0.0747,'from_image':729}

    def tearDown(self):
        self.obj1.session.close()
        self.obj2.session.close()
        self.obj3.session.close()
    
    def test_shootingdate_list(self):
        shooting_date_list_1 = self.obj1.get_shootingdate_list()
        shooting_date_list_2 = self.obj2.get_shootingdate_list()
        shooting_date_list_3 = self.obj3.get_shootingdate_list()
        self.assertEqual(len(shooting_date_list_1),3)
        self.assertEqual(len(shooting_date_list_2),3)
        self.assertEqual(len(shooting_date_list_3),3)
    
    def test_asset_id_list(self):
        asset_id_list_1 = self.obj1.get_asset_id_list()
        asset_id_list_2 = self.obj2.get_asset_id_list()
        asset_id_list_3 = self.obj3.get_asset_id_list()
        self.assertEqual(asset_id_list_1[0],self.asset_id)
        self.assertEqual(asset_id_list_2[0],self.asset_id)
        self.assertEqual(asset_id_list_3[0],self.asset_id)
    
    def test_point_data_from_assetid(self):
        asset_id_point_data_1 = self.obj1.get_point_data_from_assetid(self.asset_id)
        asset_id_point_data_2 = self.obj2.get_point_data_from_assetid(self.asset_id)
        asset_id_point_data_3 = self.obj3.get_point_data_from_assetid(self.asset_id)
        self.assertEqual(asset_id_point_data_1[0],self.b2_1['from_asset_id'])
        self.assertEqual(asset_id_point_data_2[0],self.b2_2['from_asset_id'])
        self.assertEqual(asset_id_point_data_3[0],self.b2_3['from_asset_id'])

    def test_computed_point_data(self):
        computed_mean_point_data_1 = self.obj1.get_computed_point_data()
        computed_mean_point_data_2 = self.obj2.get_computed_point_data()
        computed_mean_point_data_3 = self.obj3.get_computed_point_data()
        self.assertEqual(computed_mean_point_data_1[0]['data']['B2'],self.b2_1['from_computed_mean'])
        self.assertEqual(computed_mean_point_data_2[0]['data']['B2'],self.b2_2['from_computed_mean'])
        self.assertEqual(computed_mean_point_data_3[0]['data']['B2'],self.b2_3['from_computed_mean'])

    def test_point_gdf(self):
        point_gdf_1 = self.obj1.get_point_gdf()
        point_gdf_2 = self.obj2.get_point_gdf()
        point_gdf_3 = self.obj3.get_point_gdf()
        self.assertEqual(point_gdf_1['B2'].loc[0],self.b2_1['from_computed_mean'])
        self.assertEqual(point_gdf_2['B2'].loc[0],self.b2_2['from_computed_mean'])
        self.assertEqual(point_gdf_3['B2'].loc[0],self.b2_3['from_computed_mean'])

if __name__ == "__main__":
    unittest.main()