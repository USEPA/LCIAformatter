---
title: 'LCIA Formatter'
tags:
  - life cycle assessment
  - impact assessment
  - Python
authors:
  - name: Ben Young
    orcid: 0000-0001-6276-8670
    affiliation: 1
  - name: Michael Srocka
    orcid:
    affiliation: 2
  - name: Wesley Ingwersen^[Corresponding author]
    orcid: 0000-0002-9614-701X
    affiliation: 3
  - name: Ben Morelli
    orcid:
    affiliation: 1
  - name: Sarah Cashman
    orcid: 0000-0001-9859-9557
    affiliation: 1
  - name: Andrew Henderson
    orcid: 0000-0003-2436-7512
    affiliation: 1
affiliations:
 - name: Eastern Research Group, Inc. 
   index: 1
 - name: GreenDelta
   index: 2
 - name: U.S. Environmental Protection Agency
   index: 3
date: 15 March 2021
bibliography: paper.bib
---

# Summary

Overview and highlight relationship to other ecosystem LCA tools-Sarah

# Statement of need

Life cycle impact assessment (LCIA) methods can be implemented in life cycle assessment (LCA) software to provide impact assessment results for life cycle inventory (LCI) data loaded into the software, but the flows used in these methods must match exactly the flows in the LCI data (add ref). As LCI flows are updated, the impact methods should also be made available, and vice versa, as LCIA method developers update characterization factors, they should be available as soon as possible to work with existing LCI data. The LCIA formatter module this paper describes is a specific solution to take LCIA methods from original providers, map them to an authoritative flow list, and export them in common data formats.

# Structure

The code is written in the Python 3.x language and primarily uses the latest pandas package for data storage and manipulation. The code is stored on a USEPA GitHub repository and is available for public access.

The LCIAformatter access source methods directly from the data provider. These methods take the format of excel files or access databases. Source data are downloaded and saved in a temporary cache.
To support the specific functions necessary to access and parse individual methods, each method is processed within its own module. Flow names, indicators, characterization factors, and other metadata are compiled in a [standard format](https://github.com/USEPA/LCIAformatter/tree/documentation/format%20specs).
Adjustments are made as needed to improve consistency between indicators and across methods. This includes handling duplicate entries for the same elementary flow, data cleaning (such as cleaning string names, adjusting capitalization, formatting of CAS Registry Numbers).
Additionally, the LCIAformatter supports the inclusion of non specified secondary contexts (emission locations) where none are provided.
Where methods provide both midpoint and endpoint categories within a single source, the LCIAformatter parses these methods for separate use.
Finally, source flow data are mapped to elementary flows in the Federal Elementary Flow List [cite], through mapping files provided within that package. These mapping files correspond flow names and contexts to a common set of elementary flows generated for life cycle assessment modeling by the US EPA.
Mapped methods are stored locally as parquet files for future access by LCIAformatter or other tools.
Additionally, mapped methods can be exported as JSON-LD format for use in LCA software tools such as openLCA.


# Available Methods

## TRACI2.1 - Sarah
TRACI 2.1 source file: https://www.epa.gov/sites/production/files/2015-12/traci_2_1_2014_dec_10_0.xlsx
Source citation: [@bare_traci_2011]

## ReCiPe2016 
ReCiPe 2016 characterizes impacts across XX midpiont indicators and three perspectives: Individualist, Hierarchist, and Egalitarian [@huijbregts_recipe_2017]. The LCIAformatter generates endpoint impacts through a series of midpoint conversion factors provided for each indicator.
As is done for TRACI2.1, where characterization factors are not supplied for unspecified secondary contexts, an average factor across the possible contexts is generated. This ensures that users that do not specify a secondary context (e.g. emission/air with no indication of population density) can still obtain a characterization factor for a flow. 


## ImpactWorld+
ImpactWorld+ v1.3 is downloaded as an Access database and global flows are read into a pandas dataframe at midpoint and endpoint levels [@bulle_impact_2019]. Flows at native resolution or aggregated by landmass (continent, country, etc.) are currently excluded as they are not compatible with the FEDEFL at this time. Context information is added for water scarcity and availability categories, flowable name is applied as context for land occupation and transformation categories. Context descriptions are provided in the original source for all other categories.


## FEDEFL Inventory Methods
The LCIAformatter generates life cycle inventory methods based on groups of elementary flows identified in the FEDEFL. For example, an inventory method for energy resource use would represent a summation of all instances of these flows within a dataset. Where necessary unit conversions are applied to achieve a consistent indicator unit. 

# Applications

Valuation and other Endpoint Methods - Andrew
The LCIAformatter also includes a method-agnostic approach to convert indicators (midpoint or endpoint) to monetary values.  The primary valuation is based on budget constraint modeling [@weidema_valuation_2009], updated to USD2014; conversions between the different ecosystem impact indicators (e.g., PDF.m2.yr and species.yr) are based on the species density calculations ReCiPe 2008 [@goedkoop_recipe_2009].

The LCIA methods generated by the LCIAformatter for use with the FEDEFL are hosted publicly on the Federal LCA Commons for use by practitioners and researchers. These methods support life cycle assessments performed by many parties, including member agencies for the Federal LCA Commons such as U.S. EPA, U.S. DOE, USDA, DOD, and others. These methods also enable impact assessment for researchers utilizing the US Life Cycle Inventory (USLCI) Database.
As a Python-based package, the LCIAformatter can also be accessed by the expanding network of publicly available tools for LCA automation, including [useeior](https://github.com/USEPA/useeior) and the Electricity Life Cycle Inventory ([electricitylci](https://github.com/USEPA/ElectricityLCI)).
The system was built to be flexible enough to support creating outputs for LCIA spatially-explicit characterization factors.



# Acknowledgements

We acknowledge contributions from 

# References