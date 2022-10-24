import glob,os,shutil,sys,unittest

# 上位インポート先を追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sentinelimagerest import SentinelImageREST

# class TestSentinelImageREST(unittest.TestCase):

#     def setUp(self):
#         # test data
#         self.coords = [[
#                 [143.25916964884624, 43.20577096289138],
#                 [143.26094227838942, 43.20555456719537],
#                 [143.26087310260237, 43.20523102268399],
#                 [143.26029087306136, 43.205304555678175],
#                 [143.25992770017933, 43.20364478937389],
#                 [143.258711359257, 43.20378765711047],
#                 [143.25916964884624, 43.20577096289138]
#             ]]
#         self.start_date = '2021-07-16'
#         self.end_date = '2021-07-21'
#         self.cloudy_pixel_percentage_limit = 100
#         self.field_name = 'test'
#         self.obj = SentinelImageREST(self.coords, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit,self.field_name)
        
#         self.output_vi_dir = './vi_dir/'
#         self.output_raw_dir = './raw_dir/'
#         self.output_tc_dir = './tc_dir/'
#         self.output_assetid_dir = './assetid_dir/'

#         try:
#             os.makedirs(self.output_vi_dir)
#         except FileExistsError as e:
#             print(e)

#         try:
#             os.makedirs(self.output_raw_dir)
#         except FileExistsError as e:
#             print(e)

#         try:
#             os.makedirs(self.output_tc_dir)
#         except FileExistsError as e:
#             print(e)

#         try:
#             os.makedirs(self.output_assetid_dir)
#         except FileExistsError as e:
#             print(e)

#     def tearDown(self):
#         self.obj.session.close()
#         shutil.rmtree(self.output_vi_dir)
#         shutil.rmtree(self.output_raw_dir)
#         shutil.rmtree(self.output_tc_dir)
#         shutil.rmtree(self.output_assetid_dir)
    
#     def test_shootingdate_list(self):
#         shooting_date_list = self.obj.get_shootingdate_list()
#         self.assertEqual(len(shooting_date_list),3)
    
#     def test_geotiff_raw(self):
#         self.obj.get_geotiff_raw(self.output_raw_dir)
#         img_list = glob.glob(self.output_raw_dir + '/*')
#         for img in img_list:
#             self.assertEqual('tif',img[-3:])
            
#     def test_geotiff_vi(self):
#         self.obj.get_geotiff_vi('NDVI',self.output_vi_dir,10)
#         img_list = glob.glob(self.output_vi_dir + '/*')
#         for img in img_list:
#             self.assertEqual('tif',img[-3:])

#     def test_geotiff_tc(self):
#         self.obj.get_geotiff_tc(self.output_tc_dir,-10)
#         img_list = glob.glob(self.output_tc_dir + '/*')
#         for img in img_list:
#             self.assertEqual('tif',img[-3:])
        
#     def test_asset_id_list(self):
#         asset_id_list = self.obj.get_asset_id_list()
#         self.assertEqual(asset_id_list[0],'COPERNICUS/S2_SR_HARMONIZED/20210716T012701_20210716T012658_T54TXN')

#     def test_geotiff_raw_assetid(self):
#         self.obj.get_geotiff_raw_from_assetid(self.output_assetid_dir)
#         img_list = glob.glob(self.output_assetid_dir + '/*')
#         for img in img_list:
#             self.assertEqual('tif',img[-3:])

#     def test_vi_meshpolygon(self):
#         gdf = self.obj.create_vi_meshpolygon(self.coords,'EVI2',self.obj.get_shootingdate_list())
#         self.assertTrue(len(gdf) > 0)
        
# if __name__ == "__main__":
#     unittest.main()