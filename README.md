# Home Assistant custom sensors

## IKEA Availability sensor
This sensor retrieves the number of available units in stock of a product at the specified IKEA store. Use it to trigger a notification when a product is back in stock or similar.

### Installation
Copy the [ikea.py](https://github.com/psvanstrom/hass/blob/master/custom_components/sensor/ikea.py) script to your custom components directory: `<HASS_DIR>/custom_components/sensor`.

### Configuration
Add an IKEA availability sensor using the sensor platform:

```
sensor:
  - platform: ikea
    product_id: 40364748
    store: '012'
    url_locale: se/sv
    friendly_name: Trådfri wireless control outlet
```

#### Configuration variables
**product_id**<br/>
&nbsp;&nbsp;&nbsp;(*string*) (*Required*) The id of the product you want to monitor. You will find the product id<br/>
&nbsp;&nbsp;&nbsp;in the URL of the product page on ikea.com, example: `https://www.ikea.com/se/sv/catalog/products/<product_id>`

**store**<br/>
&nbsp;&nbsp;&nbsp;(*string*) (*Required*) The id of the store to check availability in. Some countries are available [here](https://github.com/psvanstrom/hass/blob/master/ikea_store_ids.md), but if your country is<br/>
&nbsp;&nbsp;&nbsp;missing, retrieve your store id from the HTML of the availability drop down list on the product page at IKEA.<br/>
&nbsp;&nbsp;&nbsp;**Note:** use single quotes around the store_id to make sure it gets interpreted as a string and not a number.

**url_locale**<br/>
&nbsp;&nbsp;&nbsp;(*string*) (*Required*) The locale to use in the URL when querying IKEA. Check your country specific IKEA website URL<br/>
&nbsp;&nbsp;&nbsp;Examples: `sv/se` - Sweden. `fi/fi` - Finland, and so on.

**friendly_name**<br/>
&nbsp;&nbsp;&nbsp;(*string*) (*Optional*) Give the sensor a friendly name, otherwise it will be named `ikea_<product_id>`

### Notes
The sensor will update its value every 5 minutes. However, it's unclear how often IKEA updates the values reported through their API.
