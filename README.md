# noaa_parser
Parse XML results from NOAA forecast map and output to compact XML format

## Usage
./noaa_parser.py [lat] [lon]

Note: If latitude and longitude are not specified, the parser will default to Pittsburgh PA.

## Input document

An example input document is [here](http://forecast.weather.gov/MapClick.php?lat=37.9733&lon=-122.0358&FcstType=digitalDWML).  

## Output XML example
```xml
<?xml version="1.0" ?>
<output>
	<location>point1</location>
	<hightemp>64</hightemp>
	<lowtemp>43</lowtemp>
</output>
```
