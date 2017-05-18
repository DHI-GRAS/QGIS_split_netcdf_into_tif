#Definition of inputs and outputs
#==================================
##NetCDF Tools=group
##Split netCDF into GeoTIFFs=name
##ParameterFile|ncfnames|NetCDF file to split|False|False|nc
##ParameterFile|outdir|Output directory|True|False

import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(scriptDescriptionFile), "modules"))
from split_netcdf_mod import main_multifile

ncfnames_list = ncfnames.split(';')

main_multifile(ncfnames_list, outdir,
    fname_fmt='%Y%m%d0000.tif',
    unscale=True,
    progress=progress,
    skip_existing=True)
