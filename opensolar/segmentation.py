import datetime
from dataclasses import dataclass

import cv2
import numpy as np
import requests
import streamlit as st

from opensolar.algorithms import panel_energy

angles = {
    "N": 0,
    "NNE": 22,
    "NE": 45,
    "ENE": 67,
    "E": 90,
    "ESE": 112,
    "SE": 135,
    "SSE": 157,
    "S": 180,
    "SSW": 202,
    "SW": 225,
    "WSW": 247,
    "W": 270,
    "WNW": 292,
    "NW": 315,
    "NNW": 337,
}


@st.cache_data
def get_google_maps_image(
    latitude: float,
    longitude: float,
    api_key: str,
    zoom: int = 12,
    maptype: str = "satellite",
    image_size_px: int = 400,
) -> np.ndarray:
    """Given latitude and longitude give the image as numpy array.

    For further usage see: https://developers.google.com/maps/documentation/maps-static/overview

    Args:
        latitude (float): The latitude.
        longitude (float): The longitude.
        api_key (str): The google cloud api key.
        zoom (int, optional): The ammount of zoom, larger value more zoom. Defaults to 12.
        maptype (str, optional): The type of the map. Defaults to "satellite".
        image_size_px (int, optional): The width and height of the image. Defaults to 400.

    Returns:
        np.ndarray: The image as numpy array of shape (image_size_px, image_size_px, 3)
    """
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom={zoom}&maptype={maptype}&size={image_size_px}x{image_size_px}&key={api_key}"
    response = requests.get(url).content
    image = cv2.imdecode(np.frombuffer(response, np.uint8), cv2.IMREAD_UNCHANGED)
    return image


down_scale_orientation = {
    "N": 0.7,
    "NNE": 0.74,
    "NE": 0.78,
    "ENE": 0.82,
    "E": 0.85,
    "ESE": 0.89,
    "SE": 0.92,
    "SSE": 0.95,
    "S": 1.0,
    "SSW": 0.95,
    "SW": 0.92,
    "WSW": 0.89,
    "W": 0.85,
    "WNW": 0.82,
    "NW": 0.78,
    "NNW": 0.74,
}


@dataclass
class Roof:
    orientation: str
    num_solar_panels: int
    area_per_panel: float = 1.8974
    cost_per_panel: float = 174

    @property
    def default_kWh(self):
        return 2.94 * down_scale_orientation[self.orientation]

    @property
    def tilt_angle(self) -> float:
        # TODO make that better and complete, lookup
        return angles[self.orientation]

    @property
    def total_area(self) -> float:
        return self.num_solar_panels * self.area_per_panel


def get_production_metric(
    roofs: list,
    ratios: list,
):
    total = sum([roof.num_solar_panels * roof.default_kWh for roof in roofs])
    current = 0
    for roof, ratio in zip(roofs, ratios, strict=True):
        current += roof.num_solar_panels * ratio * roof.default_kWh
    delta = (current / total) * 100
    return total, current, delta


def get_cost_metric(
    roofs: list[Roof],
    ratios: list,
):
    total = sum([roof.num_solar_panels * roof.cost_per_panel for roof in roofs])
    current = 0
    for roof, ratio in zip(roofs, ratios, strict=True):
        current += roof.num_solar_panels * ratio * roof.cost_per_panel
    delta = (1 - current / total) * 100
    return total, current, delta


@st.cache_data
def get_roof_info(image: np.ndarray) -> list[Roof]:
    # TOOD calc here the model
    roof1 = Roof(orientation="NNE", num_solar_panels=3)
    roof2 = Roof(orientation="N", num_solar_panels=2)
    return [roof1, roof2]
