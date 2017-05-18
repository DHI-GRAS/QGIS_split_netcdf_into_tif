"""Help functions for working with netCDF files"""

import datetime
import numpy as np

def _test_nc_time_defaults(timevar):
    """Test whether the netCDF time variable `timevar` has default units and calendar

    Raises
    ------
    ValueError if timevar does not have default units and calendar
    """
    if not (
            timevar.units in ["seconds since 1970-01-01 00:00:00", "seconds since 1970-01-01"] and
            timevar.calendar == "standard"):
        raise ValueError("This function works only for time variables created by this software.")


def date2num(dates, timevar):
    """Converts datetime `dates` to numbers to be stored in the variable `timevar`

    Parameters
    ----------
    dates : datetime.datetime or sequence of such
        dates to convert to time stamps to feed to netCDF time variable
    timevar : netCDF variable object
        source netCDF variable
        (used only for testing)

    Raises
    ------
    ValueError if timevar does not have default units and calendar
    """
    _test_nc_time_defaults(timevar)
    # Convert the timestamp from seconds since 1970 to year-DOY
    return np.asarray((np.asarray(dates) - datetime.datetime(1970,1,1)).total_seconds()).astype(int)


def num2date(datenum, timevar):
    """Convert timestamp numbers from timevar to datetime dates, checking for compatibility with timevar

    Parameters
    ----------
    datenum : float or sequence of floats
        time stamps to convert to dates (e.g. from timevar.data)
    timevar : netCDF variable object
        source netCDF variable
        (used only for testing)

    Raises
    ------
    ValueError if timevar does not have default units and calendar
    """
    _test_nc_time_defaults(timevar)
    # Convert the timestamp from seconds since 1970 to year-DOY
    dates = np.array([datetime.datetime.utcfromtimestamp(n) for n in np.array(datenum, copy=False, ndmin=1)])
    return np.squeeze(dates)[()]


def get_scale_factor(ds, varn=None, exclude=['time', 'lon', 'lat', 'crs']):
    """Get scale factor from a netcdf file

    Parameters
    ----------
    ds : open scipy.io.netcdf_file
        input file
    varn : str
        variable name
        if left out, it will be inferred
    exclude : list of str
        variables to exclude when finding
        the data variable (if varn is None)
    """
    if varn is None:
        exclude = [k.lower() for k in exclude]
        kk = [k for k in ds.variables.keys() if k.lower() not in exclude]
        if len(kk) > 1:
            raise ValueError("More than one variable names found in netCDF file: "
                             "{}. Please specify one.".format(kk))
        elif len(kk) == 1:
            varn = kk[0]
        else:
            raise ValueError("No valid data variables found in netCDF file.")
    return getattr(ds.variables[varn], 'scale_factor', 1)
