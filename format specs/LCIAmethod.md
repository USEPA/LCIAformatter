## LCIA Method Format

The standard output format for LCIA methods produced by lciafmt.
The flow name fields match those in the fedelemflowlist [FlowList](https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List/blob/master/format%20specs/FlowList.md) format

 Index | Field | Type | Required |  Note |
| ---- | ------ |  ---- | ---------| -----  |
 0 | Method | string | Y | The LCIA method name, e.g. 'Traci 2.1' |
 1 | Method UUID | string | N | ID for the method, generated if not supplied  |
 2 | Indicator | string | Y | Name of indicator, e.g. 'Acidification Potential' |
 3 | Indicator UUID| string | N | ID for the indicator, generated if not supplied |
 4 | Indicator unit | string | Y | The unit for the indicator, e.g. 'kg CO2 eq' |
 5 | Flowable | string | Y | The flow name, e.g. 'Sulfur dioxide' |
 6 | Flow UUID | string | Y | ID of the flow |
 7 | Context | string | Y | A path-like set of context compartments in the form of directionality/environmental media/environmental compartment, e.g. 'emission/air/tropophere' |
 8 | Unit | string | Y | Unit of the flow. Uses olca-ipc.py units
 9 | CAS No | string | N | CAS number
 10 | Location | string | N | Name of the location
 11 | Location UUID | string | N | ID of the location
 12 | Characterization factor | float | Y | LCIA characterization factor
 13 | Code | string | N | string abbreviation for indicator
