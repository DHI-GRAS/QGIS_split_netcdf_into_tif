import os.path
import numpy as np
from scipy.io import netcdf
import processing

import netcdf_utils

def _get_minmax(data):
    return np.min(data), np.max(data)

def _get_scaled_nodata(ds, progress):
    # take scale value from first variable that has one
    new_nodata = False
    for varn, datavar in ds.variables.iteritems():
        try:
            new_nodata = datavar._FillValue * datavar.scale_factor
            if progress is not None:
                progress.setConsoleInfo('Using scale_factor '
                        'from variable \'{}\''.format(varn))
            break
        except AttributeError:
            continue
    return new_nodata

def main_multifile(infiles, *args, **kwargs):
    "Multi-file wrapper for main function"
    # make sure ncfnames is iterable
    if not isinstance(infiles, list):
        infiles = [infiles]
    for infile in infiles:
        main(infile, *args, **kwargs)

def main(infile, outdir, fname_fmt='%Y%m%d.tif', params={},
         unscale=False, skip_existing=False, progress=None):
    """Extract all time slices from netCDF file naming them after date

    Parameters
    ----------
    ncfname : str
        path to netCDF file
    outdir : str
        output directory
    fname_fmt : str
        format string for datetime.datetime.strftime()
        that generates the target file name
        e.g. '%Y%m%d.tif' will give '20160101.tif'
    params : dict
        parameters passed to
        processing.runalg('gdalogr:translate')
    unscale : bool
        apply GDAL's -unscale option
        and also fix the nodata value
    skip_existing : bool
        skip existing files
        if False, existing files will be overwritten
    progress : QGIS progress, optional
        if run in QGIS
    """
    # set common parameters
    params = params.copy()
    params['INPUT'] = infile
    params['EXPAND'] = 0
    _common_extra = params.get('EXTRA', '')

    # get time data
    with netcdf.netcdf_file(infile, 'r') as ds:
        timevar = ds.variables['time']
        timedata = netcdf_utils.num2date(timevar.data, timevar)

        # set extent
        lonlim = _get_minmax(ds.variables['lon'].data)
        latlim = _get_minmax(ds.variables['lat'].data)
        params['PROJWIN'] = '{0[0]},{0[1]},{1[0]},{1[1]}'.format(lonlim, latlim)

        # unscale
        if unscale:
            if '-unscale' not in _common_extra:
                _common_extra += ' -unscale'
            # fixing nodata value (gdal_translate defficiency)
            new_nodata = _get_scaled_nodata(ds, progress)
            if new_nodata is not None:
                _common_extra += ' -a_nodata {}'.format(new_nodata)

    # export time slices to tif files
    for i, date in enumerate(timedata):
        # set specific parameters
        fname = date.strftime(fname_fmt)
        params['OUTPUT'] = os.path.join(outdir, fname)
        params['EXTRA'] = (_common_extra + ' -b {}'.format(i+1)).strip()

        # skip existing
        if skip_existing and os.path.exists(params['OUTPUT']):
            continue

        # run gdal_translate with parameters
        processing.runalg("gdalogr:translate", params)

        if not os.path.exists(params['OUTPUT']):
            raise ValueError('Algorithm failed. '
                    'No output file was created. '
                    'Parameters to gdalogr:translate were:\n'
                    '{}'.format(params.__repr__()))

        # log
        if progress is not None:
            progress.setConsoleInfo(
                "Time slice {} to file {}".format(date, fname))
