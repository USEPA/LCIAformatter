# LCIA formatter
The LCIA formatter is a Python 3 package for creating LCIA methods from their
original LCIA sources by converting them into [pandas](https://pandas.pydata.org/)
data frames with the following columns:

```
Index  Field                                              Type
----------------------------------------------------------------------
0      Method (e.g. 'Traci 2.1')                          str
1      Method UUID                                        str
2      Indicator, e.g. 'Acidification Potential'          str
3      Indicator UUID                                     str
4      Indicator unit, e.g. `kg SO2 eq.`                  str
5      Flow, e.g. `Sulfur dioxide`                        str
6      Flow UUID                                          str
7      Flow category (context), e.g. `air/unspecified`    str
8      Flow unit, e.g. `kg`                               str
9      CAS number of the flow                             str
10     Location                                           str
11     Location UUID                                      str
12     Characterization factor                            float
```

On these data frames, flow mappings defined in the
[Fed.LCA.Commons](https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List)
can be applied and the result can be exported to all formats supported by the
`pandas` package (Excel, CSV) or the
[openLCA JSON-LD format](https://github.com/GreenDelta/olca-schema).


## Usage

In order to use the project, first download it and install it (preferably in a
[virtual environment](https://docs.python.org/3/library/venv.html)):

```bash
$ git clone https://github.com/msrocka/lcia_formatter.git
$ cd lcia_formatter

# create a virtual environment and activate it
$ python -m venv env
$ .\env\Scripts\activate.bat

# install the requirements
$ pip install -r requirements.txt

# install the `master` master from the
# Fed.LCA Flow-List list repository
pip install git+https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List.git@master

# install the project
$ pip install -e .

# start the Python interpreter
$ python
```

### Loading method data
A data frame with the data of a method can be loaded with the respective
`get_[method name]` function

```python
import lciafmt
traci = lciafmt.get_traci()
```

This will download and cache the raw method data in a temporary folder
(`~/temp/lciafmt`). Before downloading method data, `lciafmt` will first
check if the method data are available in this cache folder. Alternatively,
a file path or web URL can be passed as arguments to the `get_*` methods
to load the data from other locations:

```python
traci = lciafmt.get_traci(file="path/to/traci_2.1.xlsx")
traci = lciafmt.get_traci(url="http://.../path/to/traci_2.1.xlsx")
```

Also, it is possible to clear the cache to ensure that the newest version is
downloaded from the internet:

```python
lciafmt.clear_cache()
traci = lciafmt.get_traci()
```


### Apply flow mappings
The flow mappings defined in the
[Fed.LCA.Commons](https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List)
can be directly applied on a data frame with method data:

```python
traci_mapped = lciafmt.map_flows(traci)
```

This will apply the mapping to the default Fed.LCA.Commons flow list and produce
a new data frame with mapped flows. A specific source system can be selected via
the respective parameter:

```python
traci_mapped = lciafmt.map_flows(traci, system="TRACI2.1")
```

Also, it is possible to directly pass a data frame that sepecifies a mapping
in the Fed.LCA.Commons format into the function:

```python
traci_mapped = lciafmt.map_flows(traci, mapping=a_data_frame)
```

### Data export
The converted method data are stored in a standard
[pandas data frame](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html)
so that the standard export functions of pandas can be directly used:

```python
traci.to_csv("out/traci_2.1.csv", index=False)
```

Additionally, a method can be stored as JSON-LD package that can be imported
into an openLCA database:

```python
lciafmt.to_jsonld(traci, "out/traci_2.1_jsonld.zip")
```

When also elementary flows should be written to the JSON-LD package the
`write_flows` flag can be passed to the export call:

```python
lciafmt.to_jsonld(traci, "out/traci_2.1_jsonld.zip", write_flows=True)
```

**Note** that unit groups and flow properties are currently not added to the
JSON-LD package so that the package can only be imported into a database where
at least the standard openLCA unit groups and flow properties are available.

### Logging details
The `lciafmt` module writes messages to the default logger of the `logging`
package. In order to see more details, you can set the log level to a finer
level:

```python
import logging as log
log.basicConfig(level=log.INFO)
```

## License
This project is in the worldwide public domain, released under the
[CC0 1.0 Universal Public Domain Dedication License](https://creativecommons.org/publicdomain/zero/1.0/).

![Public Domain Dedication](https://licensebuttons.net/p/zero/1.0/88x31.png)
