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

    def submit_movie_request(call):
        """Submit request for movie."""
        name = call.data.get("name")
        movies = ombi.search_movie(name)
        if movies:
            ombi.request_movie(movies[0]["theMovieDbId"])

    def submit_tv_request(call):
        """Submit request for TV show."""

        name = call.data.get("name")
        tv_shows = ombi.search_tv(name)

        if tv_shows:
            first_season = call.data.get("first_season")
            latest_season = call.data.get("latest_season")
            all_seasons = call.data.get("all_seasons")

            request_first = True if isinstance(first_season, bool) and first_season else False
            request_latest = True if isinstance(latest_season, bool) and latest_season else False
            request_all = True if isinstance(all_seasons, bool) and all_seasons else False

            _LOGGER.warning(tv_shows[0])

            ombi.request_tv(
                tv_shows[0]["id"],
                request_first=request_first,
                request_latest=request_latest,
                request_all=request_all,
            )

    def submit_music_request(call):
        """Submit request for music."""
        name = call.data.get("name")
        music = ombi.search_music_album(name)
        if music:
            ombi.request_movie(music[0]["foreignAlbumId"])

    hass.services.register(DOMAIN, "submit_movie_request", submit_movie_request)
    hass.services.register(DOMAIN, "submit_tv_request", submit_tv_request)
    hass.services.register(DOMAIN, "submit_music_request", submit_music_request)
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    return True
