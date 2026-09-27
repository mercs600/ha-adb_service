"""ADB Service – sterowanie tunerem ADB (NC+) przez HTTP API.

Zmiana 2026-09-25 (Claude): jeśli tuner nie odpowiada przy starcie HA
(np. po zaniku prądu), integracja NIE kończy się błędem, tylko:
  * rejestruje usługę adb_service.press od razu,
  * ponawia połączenie z tunerem co 60 s aż do skutku,
  * przy wywołaniu press próbuje połączyć się od razu, jeśli jeszcze nie była połączona.
Dzięki temu nie trzeba restartować Home Assistanta po starcie tunera.
Oryginalna wersja: __init__.py.bak_2026-09-25 (oraz historia w .git).
"""
import logging
from datetime import timedelta

import requests

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'adb_service'

ATTR_KEY = 'key'
DEFAULT_KEY = 'StandBy'

CONF_HOST = 'host'
DEFAULT_HOST = '192.168.0.174'

RETRY_INTERVAL = timedelta(seconds=60)
TIMEOUT = 5
ATTR_NAMES = (
    'internal_version',
    'external_version',
    'manufacturer',
    'model',
    'friendly_name',
    'release',
)


async def async_setup(hass, config):
    host = config[DOMAIN].get(CONF_HOST, DEFAULT_HOST)
    base = 'http://' + str(host) + ':8080'
    data = {'attributes': {}, 'ready': False, 'cancel_retry': None}

    def _fetch_status():
        response = requests.get(base + '/system/version', timeout=TIMEOUT)
        status = response.json()
        return {name: status.get(name) for name in ATTR_NAMES}

    async def _try_connect():
        try:
            attributes = await hass.async_add_executor_job(_fetch_status)
        except Exception as err:  # brak sieci, timeout, zła odpowiedź
            _LOGGER.warning('ADB: tuner %s niedostępny (%s)', host, err)
            return False
        if not attributes.get('internal_version'):
            _LOGGER.warning('ADB: tuner %s odpowiedział bez internal_version', host)
            return False
        data['attributes'] = attributes
        data['ready'] = True
        if data['cancel_retry'] is not None:
            data['cancel_retry']()
            data['cancel_retry'] = None
        hass.states.async_set('sensor.adb', '', attributes)
        _LOGGER.info('ADB: połączono z tunerem %s (%s)', host, attributes.get('model'))
        return True

    async def _retry(now):
        await _try_connect()

    def _send_key(name):
        requests.post(
            base + '/control/rcu',
            data={'Keypress': 'Key' + str(name)},
            timeout=TIMEOUT,
        )

    async def press(call):
        name = call.data.get(ATTR_KEY, DEFAULT_KEY)
        if not data['ready'] and not await _try_connect():
            raise HomeAssistantError('ADB: tuner ' + str(host) + ' niedostępny')
        try:
            await hass.async_add_executor_job(_send_key, name)
        except Exception as err:
            raise HomeAssistantError(
                'ADB: nie udało się wysłać klawisza ' + str(name) + ': ' + str(err)
            ) from err
        hass.states.async_set('sensor.adb', name, data['attributes'])

    hass.services.async_register(DOMAIN, 'press', press)

    if not await _try_connect():
        _LOGGER.warning(
            'ADB: tuner %s niedostępny przy starcie – ponawiam co %s s',
            host, int(RETRY_INTERVAL.total_seconds()),
        )
        hass.states.async_set('sensor.adb', 'niepolaczony', {})
        data['cancel_retry'] = async_track_time_interval(hass, _retry, RETRY_INTERVAL)

    return True
