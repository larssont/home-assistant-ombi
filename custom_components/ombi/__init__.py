"""Example of a custom component exposing a service."""
import logging

import voluptuous as vol

from .const import CONF_URLBASE, DOMAIN, DEFAULT_PORT, DEFAULT_URLBASE, DEFAULT_SSL

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_URLBASE, default=DEFAULT_URLBASE): cv.string,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Setup the service example component."""
    import pyombi

    urlbase = f"{config[DOMAIN][CONF_URLBASE].strip('/') if config[DOMAIN][CONF_URLBASE] else ''}/"

    ombi = pyombi.Ombi(
        ssl=config[DOMAIN][CONF_SSL],
        host=config[DOMAIN][CONF_HOST],
        port=config[DOMAIN][CONF_PORT],
        api_key=config[DOMAIN][CONF_API_KEY],
        username=config[DOMAIN][CONF_USERNAME],
        urlbase=urlbase,
    )

    try:
        ombi.test_connection()
    except pyombi.OmbiError as err:
        _LOGGER.warning("Unable to setup Ombi: %s", err)
        return

    hass.data[DOMAIN] = {"instance": ombi}

    def send_request(call):
        """My first service."""

        def request_media(query, search, request, media_db):
            media = search(query)
            if media:
                media_id = media[0][media_db]
                request(media_id)

        media_type = call.data.get("type")
        name = call.data.get("name")

        if media_type == "tv":
            request_media(name, ombi.search_tv, ombi.request_tv, "theTvDbId")
        elif media_type == "movie":
            request_media(name, ombi.search_movie, ombi.request_movie, "theMovieDbId")
        elif media_type == "music":
            request_media(name, ombi.search_music_album, ombi.request_music, "albumId")

    hass.services.register(DOMAIN, "submit_request", send_request)
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    return True
