# LCIA formatter
The LCIA formatter is a Python 3 package for creating LCIA methods from their
original sources by converting them into a [pandas](https://pandas.pydata.org/)
data frame in the [LCIAmethod format](./format%20specs/LCIAmethod.md).

Flow mappings as defined in the
[Fed.LCA.Commons](https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List)
can be applied and the result can be exported to all formats supported by the
`pandas` package (e.g. Excel, CSV) or the
[openLCA JSON-LD format](https://github.com/GreenDelta/olca-schema).

See the [Wiki](https://github.com/USEPA/LCIAformatter/wiki/) for installation and use instructions.

## Disclaimer
The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis
 and the user assumes responsibility for its use.  EPA has relinquished control of the information and no longer
  has responsibility to protect the integrity , confidentiality, or availability of the information.  Any
   reference to specific commercial products, processes, or services by service mark, trademark, manufacturer,
    or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA.  The EPA seal
     and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or
      the United States Government.
