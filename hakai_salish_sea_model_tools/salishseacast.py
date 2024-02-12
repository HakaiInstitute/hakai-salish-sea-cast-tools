import xarray as xr
import requests
from pathlib import Path
from loguru import logger
import numpy as np

SALISHSEACAST_ERDDAP = "https://salishsea.eos.ubc.ca/erddap"
NEMO_MODEL_GRID_DATASET_ID = "ubcSSnBathymetryV21-08"
GRID_FILE = "nemo_grid_dataset_geo.nc"

class NEMOGrid:
    def __init__(self):
        self.dataset = None
        self.erddap = "https://salishsea.eos.ubc.ca/erddap"
        self.dataset_id=  "ubcSSnBathymetryV21-08"
        self.url = f"{self.erddap}/griddap/{self.dataset_id}.nc"
        self.local_file =  Path("nemo_grid_dataset_geo.nc")
        self.get_dataset()

    def get_dataset(self):
        """
        Get the dataset from the ERDDAP server
        """
        if not self.local_file.exists():
            logger.info("Retrieve dataset from ERDDAP server")
            with requests.get(self.url) as r:
                r.raise_for_status()
                with open(GRID_FILE,"wb") as f:
                    f.write(r.content)
        
        self.dataset = xr.open_dataset(GRID_FILE)
    @logger.catch(default=None)
    def ll2grid(self,latitude,longitude, min_depth=None, output=None) -> xr.Dataset:
        """Retrieve NEMO model grid node from latitude and longitude"""
        if self.dataset is None:
            self.get_dataset()
        if min_depth:
            dataset = self.dataset.where(self.dataset.bathymetry > min_depth)
        else:   
            dataset = self.dataset

        lat = dataset.latitude.values
        lon = dataset.longitude.values
        distance = self.latlong_to_distance((lat,lon),(latitude,longitude))
        j,i = np.unravel_index(np.nanargmin(distance),lat.shape)
        node = self.dataset.sel(gridY=j,gridX=i)
        if output is None:
            return (node,distance[j,i])
        elif output == 'dict':
            return {
                **{coord: node[coord].item(0) for coord in node.coords},
                **{name:var.item(0) for name,var in node.variables.items()},
                "distance": distance[j,i]
            }

    @staticmethod
    def latlong_to_distance(position,position2):
        """Compute the distance between two points on the Earth's surface where position= (latitude,longitude) in degrees """
        lat1, lon1 = position
        lat2, lon2 = position2
        R = 6371  # Radius of the Earth in km
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c
    