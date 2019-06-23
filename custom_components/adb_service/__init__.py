import json
import requests

DOMAIN = 'adb_service'

ATTR_KEY = 'key'
DEFAULT_KEY = 'StandBy'

CONF_HOST = 'host'
DEFAULT_HOST = '192.168.0.174'


def setup(hass, config):
    host = config[DOMAIN].get(CONF_HOST, DEFAULT_HOST)
    statusResponse = requests.get('http://' + str(host) + ':8080/system/version')
    statusResponse = statusResponse.json()
    attributes = {
        'internal_version': statusResponse.get('internal_version'),
        'external_version': statusResponse.get('external_version'),
        'manufacturer': statusResponse.get('manufacturer'),
        'model': statusResponse.get('model'),
        'friendly_name': statusResponse.get('friendly_name'),
        'release': statusResponse.get('release')
    }

    def press(call):
        name = call.data.get(ATTR_KEY, DEFAULT_KEY)
        address = 'http://' + str(host) + ':8080/control/rcu'
        response = requests.post(address, data={'Keypress': 'Key' + str(name)})
        hass.states.set('sensor.adb', name, attributes)

    if statusResponse.get('internal_version'):
        hass.states.set('sensor.adb', '', attributes)
        hass.services.register(DOMAIN, 'press', press)
    else:
        return False

    return True