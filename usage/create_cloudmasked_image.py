import rasterio as rio
import numpy as np

file_path = './sampleimage/sample_CLDMASK.tif'

with rio.open(file_path) as src:
    dataset = src.read()

b2 = dataset[0].astype(np.float32)
b3 = dataset[1].astype(np.float32)
b4 = dataset[2].astype(np.float32)
b8 = dataset[3].astype(np.float32)
b11 = dataset[4].astype(np.float32)
cldmask = dataset[7]

ndvi = (b8 - b4) / (b8 + b4)
evi2 = (2.5 * (b8 - b4)) / (b8 + 2.4 * b4 + 10000)
ndwi = (b4-b11)/(b4+b11)

ndvi_cldmasked = np.where(cldmask == 1, np.nan, ndvi)
evi2_cldmasked = np.where(cldmask == 1, np.nan, evi2)
ndwi_cldmasked = np.where(cldmask == 1, np.nan, ndwi)

kwargs = src.meta
kwargs.update(
    dtype=rio.float32,
    nodata=np.nan,
    count=1,
    compress='lzw'
)

save_path = './sampleimage/masked_ndvi.tif'
with rio.open(save_path,mode='w',**kwargs) as src:
    src.write(ndvi_cldmasked,1)

save_path = './sampleimage/masked_evi2.tif'
with rio.open(save_path,mode='w',**kwargs) as src:
    src.write(evi2_cldmasked,1)

save_path = './sampleimage/masked_ndwi.tif'
with rio.open(save_path,mode='w',**kwargs) as src:
    src.write(ndwi_cldmasked,1)