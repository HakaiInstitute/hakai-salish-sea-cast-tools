from hakai_salish_sea_model_tools import salishseacast
import pytest
import xarray as xr

nemo_grid = salishseacast.NEMOGrid()

@pytest.mark.parametrize("lat,long",[(49.0,-123.0)])
def test_salishseacast_ll2grid(lat,long):
    """
    Test conversion of lat/lon to SalishSeaCast NEMO model grid indices
    """
    data,distance = nemo_grid.ll2grid(lat,long)
    assert isinstance(data,xr.Dataset)
    assert abs(data.latitude.values - lat) < 0.1
    assert abs(data.longitude.values - long) < 0.1

