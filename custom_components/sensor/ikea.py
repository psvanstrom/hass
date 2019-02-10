"""
Support for IKEA product availability
"""
import logging
import voluptuous as vol
import requests
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_FRIENDLY_NAME)
from homeassistant.components.sensor import (PLATFORM_SCHEMA, ENTITY_ID_FORMAT)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle, slugify

REQUIREMENTS = ['xmltodict==0.11.0']
  
_LOGGER = logging.getLogger(__name__)

TIME_BETWEEN_UPDATES = timedelta(minutes=5)

ATTRIBUTION = 'Data provided by ikea.com'
USER_AGENT = "Home Assistant IKEA sensor"
CONF_PRODUCT = 'product_id'
CONF_STORE = 'store'
CONF_URL_LOCALE = 'url_locale'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PRODUCT): cv.string,   
    vol.Required(CONF_STORE): cv.string,
    vol.Required(CONF_URL_LOCALE): cv.string,
    vol.Optional(CONF_FRIENDLY_NAME): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    product_id = config.get(CONF_PRODUCT)
    store_id = config.get(CONF_STORE)
    url_locale = config.get(CONF_URL_LOCALE)
    name = 'IKEA - {}'.format(product_id)
    friendly_name = config.get(CONF_FRIENDLY_NAME, name)

    _LOGGER.debug("Setting up the sensor for store %s", store_id)

    sensors = []

    sensors.append(IKEASensor(name, friendly_name, product_id, store_id, url_locale))
    
    add_entities(sensors)


class IKEASensor(Entity):
    def __init__(self, name, friendly_name, product_id, store_id, url_locale):
        self.entity_id = ENTITY_ID_FORMAT.format(slugify(name))
        self._friendly_name = friendly_name
        self._url = "https://www.ikea.com/{}/iows/catalog/availability/{}". \
                   format(url_locale, product_id)
        self._data = None
        self._product_id = product_id
        self._store_id = store_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._friendly_name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:shopping'

    @property
    def state(self):
        """Return the state of the device."""
        if self._data:
            return self._data.get('availableStock', 'n/a')
        return 'n/a'

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return "units"

    @property
    def device_state_attributes(self):
        """ Return the sensor attributes ."""

        val = {}
        val['attribution'] = ATTRIBUTION
        #val['unit_of_measurement'] = 'min'

        if self._data:
            val['in_stock_probability'] = self._data['inStockProbabilityCode']
            val['valid_date'] = self._data['validDate']
            
        return val

    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data and updates the states."""
        import xmltodict

        _LOGGER.debug("Update data for %s using %s", self.entity_id, self._url)

        try:
            req = requests.get(self._url, headers={"User-agent": USER_AGENT}, 
                allow_redirects=True, timeout=5)

        except:
            _LOGGER.error("Failed fetching IKEA availability for product '%s'", 
                self._product_id)
            return

        found = False
        if req.status_code == 200:
            doc = xmltodict.parse(req.text)
            for store in doc['ir:ikea-rest']['availability']['localStore']:
                if store['@buCode'] == self._store_id:
                    found = True
                    self._data = store['stock']
        else:
            _LOGGER.error("Failed fetching IKEA availability for product '%s', server returned HTTP %d", 
                self._product_id, req.status_code)

        if not found:
            _LOGGER.error("Could not find store '%s' in server response", self._store_id)

