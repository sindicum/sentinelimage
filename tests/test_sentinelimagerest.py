# 上位インポート先を追加
import glob,os,shutil,sys,unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sentinelimagerest.sentinelimagerest import SentinelImageREST

class TestSentinelImageREST(unittest.TestCase):

    def setUp(self):
        # test data
        self.coords = [[
                [143.25916964884624, 43.20577096289138],
                [143.26094227838942, 43.20555456719537],
                [143.26087310260237, 43.20523102268399],
                [143.26029087306136, 43.205304555678175],
                [143.25992770017933, 43.20364478937389],
                [143.258711359257, 43.20378765711047],
                [143.25916964884624, 43.20577096289138]
            ]]
        self.start_date = '2021-07-16'
        self.end_date = '2021-07-21'
        self.cloudy_pixel_percentage_limit = 100
        
        self.output_vi_dir = './vi_dir/'
        self.output_raw_dir = './raw_dir/'
        self.output_tc_dir = './tc_dir/'
        self.output_assetid_dir = './assetid_dir/'
        
        self.field_name = 'test'
        
        self.obj_vi = SentinelImageREST(self.coords, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit,self.output_vi_dir,self.field_name)
        self.obj_raw = SentinelImageREST(self.coords, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit,self.output_raw_dir,self.field_name)
        self.obj_tc = SentinelImageREST(self.coords, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit,self.output_tc_dir,self.field_name)
        self.obj_assetid = SentinelImageREST(self.coords, self.start_date, self.end_date, self.cloudy_pixel_percentage_limit,self.output_assetid_dir,self.field_name)

        try:
            os.makedirs(self.output_vi_dir)
        except FileExistsError as e:
            print(e)

        try:
            os.makedirs(self.output_raw_dir)
        except FileExistsError as e:
            print(e)

        try:
            os.makedirs(self.output_tc_dir)
        except FileExistsError as e:
            print(e)

        try:
            os.makedirs(self.output_assetid_dir)
        except FileExistsError as e:
            print(e)


    def tearDown(self):
        self.obj_vi.session.close()
        self.obj_raw.session.close()
        self.obj_tc.session.close()
        self.obj_assetid.session.close()
        # ファイル削除
        shutil.rmtree(self.output_vi_dir)
        shutil.rmtree(self.output_raw_dir)
        shutil.rmtree(self.output_tc_dir)
        shutil.rmtree(self.output_assetid_dir)
    
    def test_shootingdate_list(self):
        shooting_date_list = self.obj_vi.get_shootingdate_list()
        self.assertEqual(len(shooting_date_list),3)
    
    def test_geotiff_raw(self):
        self.obj_raw.get_geotiff_raw()
        img_list = glob.glob(self.output_raw_dir + '/*')
        for img in img_list:
            self.assertEqual('tif',img[-3:])
            
    def test_geotiff_vi(self):
        self.obj_vi.get_geotiff_vi('NDVI',10)
        img_list = glob.glob(self.output_vi_dir + '/*')
        for img in img_list:
            self.assertEqual('tif',img[-3:])

    def test_geotiff_tc(self):
        self.obj_tc.get_geotiff_tc(-10)
        img_list = glob.glob(self.output_tc_dir + '/*')
        for img in img_list:
            self.assertEqual('tif',img[-3:])
        
    def test_asset_id_list(self):
        asset_id_list = self.obj_assetid.get_asset_id_list()
        self.assertEqual(asset_id_list[0],'COPERNICUS/S2_SR_HARMONIZED/20210716T012701_20210716T012658_T54TXN')

    def test_geotiff_raw_assetid(self):
        self.obj_assetid.get_geotiff_raw_with_assetid(self.output_assetid_dir)
        img_list = glob.glob(self.output_assetid_dir + '/*')
        for img in img_list:
            self.assertEqual('tif',img[-3:])

    def test_vi_meshpolygon(self):
        gdf = self.obj_vi.create_vi_meshpolygon('EVI2')
        self.assertTrue(len(gdf) > 0)
    
    def test_get_numpy_tc(self):
        shooting_date_list = self.obj_tc.get_shootingdate_list()
        np_arr = self.obj_tc.get_numpy_tc(shooting_date_list[0])
        self.assertEqual(3,len(np_arr['image']))
        
if __name__ == "__main__":
    unittest.main()