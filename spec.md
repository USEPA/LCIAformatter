## LCIA Formatter

> The LCIA raw data will be acquired and processed from the original source so
> as to be as transparent as possible, using StEWI's acquisition of data such
> as TRI as an example.

```python
# the LCIA formatter will be a standard Python module
# that can be easily installed via pip
import lcia_formatter as lcia

# getting the current Traci / ReCiPe / ... method data
# from an official URL could look like this:
traci = lcia.get_traci()
recipe = lcia.get_recipe()

# the downloaded Excel file is cached in a temporary folder
# e.g. ~/temp/.lcia_formatter_cache; calling `get_traci` will
# first check if there is a current version in this folder;

# it is possible to clear the cache to ensure that the newest
# version is downloaded from the internet
lcia.clear_cache()
traci = lcia.get_traci()

# alternatively, the method can be directly loaded from a file
# or URL
traci = lcia.get_traci(file="../data/Traci_2.1.xlsx")
recipe = lcia.get_recipe(
  url="http://www.rivm.nl/sites/....xlsx") 

# the returned value is a pandas data frame in a defined
# format, e.g. as specified in the IO model builder;
# so all methods of pandas can be directly used, e.g.
# storing it as a CSV file:
traci.to_csv("path/to/file.csv")

# the details for converting the respective LCIA method formats
# into this data frame format will be abstracted away in the
# respective retrieval methods
```

> Existing mappings between the original LCIA source flows and the
> Fed Commons flow list flows will be integrated for use directly
> using methods in the Federal LCA Commons Flow list Python module

```python
import lcia_formatter as lcia
import fedelemflowlist as flowlist

# this will apply the default mapping from the Federal LCA Commons
# flow list module:
traci = lcia.get_traci()
lcia.map_flows(traci)

# applying a mapping of another version from the Fed.LCA flow list
# can be done by setting the version in the method call:
lcia.map_flows(traci, version="0.2")

# also, the flow mapping can be directly passed as pandas data frame
# (in the Fed.LCA flow list format) into this method:
# lcia.map_flows(traci, mapping=a_data_frame)
```

> The LCIA methods will be created in both tabular and openLCA
> JSON-LD formats or available as a pandas dataframe via method(s)
> in the _init_ module.

```python
# as described above, the `get_<method>` functions will return
# a data frame of a defined format which can be directly stored
# as CSV or Excel file: 
traci.to_excel("path/to/file.xlsx")

# the function `write_jsonld` will export the data into a
# JSON-LD package:
lcia.write_jsonld(traci, "path/to/file.zip")
```

> The system will be flexible enough to support creating outputs
> for LCIA spatially-explicit characterization factors.

```python
# the LCIA method data frame can have an optional location
# column which can be tested with the `is_regionalized`
# function:
lcia.is_regionalized(traci)

# the JSON-LD export will also create location links in the
# exported characterization factors; a possible integration
# in openLCA will be checked
```
