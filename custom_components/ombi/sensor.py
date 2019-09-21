"""Support for Ombi."""
import logging

from pyombi import OmbiError

from .const import DOMAIN, SENSOR_TYPES

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Ombi sensor platform."""
    sensors = []

    ombi = hass.data[DOMAIN]

    for sensor in SENSOR_TYPES:
        sensor_label = sensor
        sensor_type = SENSOR_TYPES[sensor]["type"]
        sensor_icon = SENSOR_TYPES[sensor]["icon"]
        sensors.append(
            OmbiSensor(sensor_label, sensor_type, ombi, sensor_icon)
        )

    add_entities(sensors, True)


class OmbiSensor(Entity):
    """Representation of an Ombi sensor."""

    def __init__(self, label, sensor_type, ombi, icon):
        """Initialize the sensor."""
        self._state = None
        self._label = label
        self._type = sensor_type
        self._ombi = ombi
        self._icon = icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Ombi {self._type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update the sensor."""
        try:
            if self._label == "pending":
                self._state = self._ombi.pending_requests
            elif self._label == "movies":
                self._state = self._ombi.movie_requests
            elif self._label == "tv":
                self._state = self._ombi.tv_requests
            elif self._label == "approved":
                self._state = self._ombi.approved_requests
            elif self._label == "available":
                self._state = self._ombi.available_requests
        except OmbiError as err:
            _LOGGER.warning("Unable to update Ombi sensor: %s", err)
            self._state = None
            return
