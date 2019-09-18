"""Support for Ombi."""
import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SSL,
)
from homeassistant.helpers.entity import Entity
import pyombi

_LOGGER = logging.getLogger(__name__)

CONF_URLBASE = "urlbase"

DEFAULT_HOST = "localhost"
DEFAULT_NAME = "Ombi"
DEFAULT_PORT = 5000
DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)
DEFAULT_SSL = False
DEFAULT_URLBASE = ""

SENSOR_TYPES = {
    "movies": {
        "type": "Movie Requests",
        "icon": "mdi:movie",
    },
    "tv": {
        "type": "TV Show Requests",
        "icon": "mdi:television-classic",
    },
    "pending": {
        "type": "Pending Requests",
        "icon": "mdi:clock-alert-outline",
    },
    "recentlyaddedmovies": {
        "type": "Recently added movies",
        "icon": "mdi:movie",
    },
    "recentlyaddedtv": {
        "type": "Recently added TV Shows",
        "icon": "mdi:television-classic",
    },
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_URLBASE, default=DEFAULT_URLBASE): cv.string,
        vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(list(SENSOR_TYPES))]
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Ombi sensor platform."""

    name = config[CONF_NAME]
    conditions = config[CONF_MONITORED_CONDITIONS]

    urlbase = f"{config[CONF_URLBASE].strip('/') if config[CONF_URLBASE] else ''}/"

    ombi = pyombi.Ombi(
        ssl=config[CONF_SSL],
        host=config[CONF_HOST],
        port=config[CONF_PORT],
        api_key=config[CONF_API_KEY],
        urlbase=urlbase,
    )

    try:
        ombi.test_connection()
    except pyombi.OmbiError as e:
        _LOGGER.warning(f"Error while setting up Ombi: {e}")
        return

    sensors = []

    for condition in conditions:
        sensor_label = condition
        sensor_type = SENSOR_TYPES[condition].get("type")
        sensor_icon = SENSOR_TYPES[condition].get("icon")
        sensors.append(OmbiSensor(name, sensor_label, sensor_type, ombi, sensor_icon))

    add_entities(sensors, True)


class OmbiSensor(Entity):
    """Representation of an Ombi sensor."""

    def __init__(self, name, label, sensor_type, ombi, icon):
        """Initialize the sensor."""
        self._state = None
        self._name = name
        self._label = label
        self._type = sensor_type
        self._ombi = ombi
        self._attributes = {}
        self._icon = icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):

        try:
            self._ombi.update()
        except pyombi.OmbiError as e:
            _LOGGER.warning(f"Error updating Ombi sensor: {e}")
            self._state = None
            return

        if self._label == "pending":
            self._state = self._ombi.pending_requests
        elif self._label == "recentlyaddedmovies":
            self._attributes = self._ombi.recently_added_movies
            self._state = len(self._attributes)
        elif self._label == "recentlyaddedtv":
            self._attributes = self._ombi.recently_added_tv
            self._state = len(self._attributes)
        elif self._label == "movies":
            self._state = self._ombi.movie_requests
        elif self._label == "tv":
            self._state = self._ombi.tv_requests
