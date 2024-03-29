## LCIA Compilation

Custom methods consisting of indicators from multiple indicators can be created using `lciafmt.generate_lcia_compilation()`. 
This requires an input `.yaml` file with the following specifications.
See [epd.yaml](../lciafmt/data/epd.yaml) for an example.

```
name: # Name given to new method
rename_indicators: # True or False
indicators: # Include as many unique indicators as desired as shown
    Climate change: # The provided indicator name will be used if `rename_indicators` is `True`
      method: IPCC # Method name from exisiting methods available in LCIAfmt
      indicator: AR5-100 # Indicator name available within the selected method
      code: GHG # (optional) code
```
