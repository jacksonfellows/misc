Download raster data: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/VPU/Current/Raster/.
Documentation for NHDPlusHR: https://pubs.usgs.gov/of/2019/1096/ofr20191096.pdf


Compile C shared library:
```sh
cc -shared -fPIC -o libflowpath.so flowpath.c
```
