#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys
import datetime
from xml.etree.ElementTree import Element, tostring

# reference URL
API_ENDPOINT = ("https://graphical.weather.gov/xml/sample_products/"
                "browser_interface/ndfdBrowserClientByDay.php"
                "?numDays=7&format=24+hourly&Unit=e")
CONFIG_TEMPLATE = \
    {
        "lat": 40.4406,
        "lon": -79.9959
    }

OUTPUT_TEMPLATE = \
    {
        "location": "None",
        "hightemp": "None",
        "lowtemp": "None",
    }


def print_help(exit_code=0):
    """Print help and also exit nonzero if specified."""
    print("Usage: noaa_parser [lat] [lon]")
    sys.exit(exit_code)


def cmdline_parser():
    """Parse options from commandline. Everything is optional."""
    args = sys.argv[1:]
    config = CONFIG_TEMPLATE

    if len(args) > 3:
        print_help(exit_code=2)

    if len(args) == 1:
        if args[0] == "--help" or args[0] == "-h":
            print_help()

    if len(args) > 0:
        try:
            config["lat"] = float(args[0])
        except Exception as e:
            print("latitude must be a float! EG: 1.10, 7.488, 10.100002")
            print_help(exit_code=2)
    if len(args) > 1:
        try:
            config["lon"] = float(args[1])
        except Exception as e:
            print("longitude must be a float! EG: 1.10, 7.488, 10.100002")
            print_help(exit_code=2)

    return config


def query_param_builder(lat=40.4406, lon=79.9959):
    """Interpolate arguments into query parameters."""
    now = datetime.datetime.now()
    date_str = "{0}-{1}-{2}".format(now.year, now.month, now.day)

    result = "&lat={0}&lon={1}&startDate={2}".format(lat, lon, date_str)
    return result


def request_weather(url):
    """Simply returns XML document from a URI"""
    try:
        r = requests.get(url)
    except Exception as e:
        print("Exception occured during API request: {}".format(e))
        print("URL requested: {}".format(url))
        sys.exit(2)
    if r.status_code > 299 or r.status_code < 200:
        print("API returned non 200 response code: {}".format(r.status_code))
        sys.exit(2)

    return r.text


def parse_weather(xml_string):
    """Returns location, high, and low temps in a dictionary"""
    output = OUTPUT_TEMPLATE

    try:
        root = ET.fromstring(xml_string)
    except Exception as e:
        print("Exception parsing XML from NOAA: {}".format(e))
        sys.exit(2)

    output['location'] = root.find('./data/location/location-key').text
    parameters = root.find('./data/parameters')

    for child in parameters:
        if child.tag == "temperature":
            # filter invalid tag attributes
            if "type" not in child.attrib:
                continue
            if child.attrib['type'] == 'maximum':
                output['hightemp'] = child.find('./value').text
            elif child.attrib['type'] == 'minimum':
                output['lowtemp'] = child.find('./value').text

    return output


def dict_to_xml(tag, d):
    """This handy function borrowed from
    https://www.safaribooksonline.com/library/view/python-cookbook-3rd/9781449357337/ch06s05.htm
    Convert dictionary to xml Elementree Elements
    """
    elem = Element(tag)
    for key, val in d.items():
        child = Element(key)
        child.text = str(val)
        elem.append(child)
    return elem


def main():
    # retrieve our options dictionary
    options = cmdline_parser()

    # set the query parameters from the options dict
    url = API_ENDPOINT + query_param_builder(**options)

    # hopefully get XML from the NOAA API
    result = request_weather(url)

    # parse only the fields we need
    output = parse_weather(result)

    # convert our python dictionary to XML
    xml_output = dict_to_xml("output", output)

    # since the xml library is 'older', we need to import a minidom
    # to pretty print
    output_pretty = xml.dom.minidom.parseString(tostring(xml_output))

    # call toprettyxml method from minidom
    print(output_pretty.toprettyxml())


if __name__ == '__main__':
    main()
