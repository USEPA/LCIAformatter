## Endpoint Method Format

The format for input data for generating endpoint LCIA methods

 Index | Field | Type | Required |  Note |
| ---- | ------ |  ---- | ---------| -----  |
 0 | Method | string | Y | The LCIA method name, e.g. 'Traci 2.1' |
 1 | Indicator | string | Y | Name of indicator, e.g. 'Acidification Potential' |
 2 | Indicator unit | string | Y | The unit for the indicator, e.g. `kg CO2 eq` |
 3 | Endpoint Indicator | string | Y | Name of the desired endpoint indicator |
 4 | Endpoint Indicator unit | string | Y | The unit for the desired endpoint indicator, e.g. `USD` |
 5 | Conversion factor | float | Y | Midpoint to endpoint conversion factor |
