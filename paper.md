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
    orcid: 0000-0002-7660-6485
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
date: 19 March 2021
bibliography: paper.bib
---

# Summary
LCA is an established and standardized methodology to comprehensively assess environmental and public health metrics across industries and products [@international_organization_for_standardization_enivronmental_2006]. The United States Environmental Protection Agency (USEPA) is developing an open source life cycle assessment (LCA) tool ecosystem [@ingwersen_lca_2019].  The ecosystem includes tools to automate the creation of life cycle inventory (LCI) datasets, which account for flows to and from nature for steps across the life cycle of products or services, and life cycle impact assessment (LCIA) tools to support classification and characterization of the cumulative LCI to potential impacts. This paper describes a USEPA LCA ecosystem tool 'LCIA formatter' that extracts LCIA information from original source methods and converts the data for interoperability with the rest of the USEPA LCA ecosystem tools.   

# Statement of need
A simplified algorithm for LCA is given in [@eq:lca], where $I$ are impacts, $E$ are emissions generated (e.g. pollutants) or raw resources consumed (e.g. land, water) per functional unit of product across the entire supporting product system and $CF$ are corresponding characterization factors that quantitatively relate a unit of a flow to a unit of a given impact indicator (ie. global warming, acidification, total land use). 
$$
I = \sum(E*CF)
$$ {#eq:lca}

 Both $E$ and $CF$ use objects called elementary flows, which are data objects that generally represent a substance (e.g. Ammonia), source or receiving environmental compartment (e.g. Freshwater lake), and unit (e.g. kilogram). $E$ will have a total quantity of a given elementary flow from the product system, and the characterization factors in $CF$ are in the form of the indicator unit per elementary flow unit (e.g. kg N-eq per kg Ammonia). E comes from the LCI calculated for the given product under user-defined conditions, and CF is a static dataset that comes from an LCIA method provider. 

LCA software generally include LCIA methods to provide impact assessment results for user-created and software-provided LCI, but the elementary flows used in these LCIA methods must be the same data objects as the flows in the LCI data to able proper impact result calculations. A major challenge to being able to reproduce LCA results and share LCA models across platforms is that there is no internationally common list of elementary flows used by either LCI, LCIA, or software providers. A critical review of elementary flow in LCA data showed that flows in LCIA methods are the least clearly described and therefore least portable and machine-readable among those from LCI, LCIA and software providers [@edelen_critical_2018]. Furthermore, LCA software providers of both proprietary and open source software have not provided an open process or external peer review of their incorporation of data from LCIA providers. This is one potential cause of discrepancies in results across LCA software.

The LCIA formatter is a specific solution to this problem. The LCIA formatter transparently acquires LCIA methods from original provider data portals, maps them to an authoritative flow list, and exports them in common data formats. The LCIA formatter v1.0 uses the Federal LCA Commons Elementary Flow List (FEDEFL) as the authoritative system of elementary flows [@edelen_federal_2019]. This system has been adopted by federal agencies in the U.S. for use in sharing data through the Federal LCA Commons [(FLCAC)](https://www.lcacommons.gov/). The automation of this process provided by the LCIAformatter is critical, because as elementary flows used in LCI are updated, the LCIA datasets should also be automatically updated, and vice versa, to facilitate their use in LCA. 

# Structure
The LCIA formatter code is written in Python 3 and created as a standard python package called `lciafmt` that can be installed using pip. The LCIA formatter primarily uses pandas for data wrangling, and the Apache parquet format for local storage of processed datasets, and olca-py for writing data in a standard LCA data format. The code is stored on a USEPA GitHub [repository](https://github.com/USEPA/LCIAformatter) and is available for public access.

The LCIA formatter accesses LCIA datasets directly from the data provider. These datasets are typically provided as Microsoft Excel or Access files. These are downloaded and saved in a temporary local cache.
To support the specific functions necessary to access and parse individual methods, each method is processed within its own module. Flow names, indicators, characterization factors, and other metadata are compiled in a [standard format](https://github.com/USEPA/LCIAformatter/tree/documentation/format%20specs).
Adjustments are made as needed to improve consistency between indicators and across methods. This includes handling duplicate entries for the same elementary flow, data cleaning (such as cleaning string names, adjusting capitalization, formatting of CAS Registry Numbers).
Additionally, the LCIA formatter supports the inclusion of non specified secondary contexts (emission locations) where none are provided.
Where methods provide both midpoint and endpoint categories within a single source, the LCIA formatter parses these methods for separate use.
Finally, source flow data are mapped to elementary flows in the FEDEFL [@edelen_federal_2019], through mapping files provided within that [package](https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List). These mapping files correspond flow names and contexts to a common set of elementary flows generated for life cycle assessment modeling by the US EPA.
Mapped methods are stored locally as parquet files for future access by LCIA formatter or other tools.
Additionally, mapped methods can be exported as JSON-LD format for use in LCA software tools such as [openLCA](https://www.openlca.org/).


# Available Methods
The LCIA formatter is structured to easily convert original source data from existing LCIA methods. Version 1.0 of the LCIA formatter converts three commonly used LCIA methods: TRACI 2.1, ReCiPe2016, and ImpactWorld+. Available LCIA methods cover a variety of impact categories, with midpoint and/or endpoint indicators available at different points on the environmental cause-effect chain [@unep_glam_2016]. Cumulative LCI indicators based on the FEDEFL are also available as an output of the LCIA formatter.

## TRACI2.1
USEPA's Tool for Reduction and Assessment of Chemicals and Other Impacts (TRACI) is widely used for LCA across the U.S. Federal Government and by U.S.-based LCA practitioners [@bare_traci_2011]. The LCIA formatter accesses the TRACI Excel-based source file and characterizes impacts across 9 midpiont indicators for use in U.S.-focused analyses. When available, flow characterization factors are mapped to the release context with the greatest level of detail. For example, an air emission may be linked to the specific release height and population density of release. If such secondary context data is unknown, the LCIA formatter generates an average factor across the possible contexts to ensure the flow will still be captured in model calculations.

## ReCiPe2016 
ReCiPe 2016 characterizes impacts across 18 midpiont indicators and three perspectives: Individualist, Hierarchist, and Egalitarian [@huijbregts_recipe_2017]. The LCIA formatter generates endpoint impacts through a series of midpoint conversion factors provided for each indicator.
As is done for TRACI2.1, where characterization factors are not supplied for unspecified secondary contexts, an average factor across the possible contexts is generated. This ensures that users that do not specify a secondary context (e.g. emission to air with no indication of population density) can still obtain a characterization factor for a flow. 

## ImpactWorld+
ImpactWorld+ v1.3 is downloaded as an Access database and read into a pandas dataframe using the pyodbc. ImpactWorld+ v1.3 provides characterization factors for indicators at midpoint and endpoint levels [@bulle_impact_2019]. Flows at native resolution or aggregated by landmass (continent, country, etc.) are currently excluded as they are not compatible with the FEDEFL at this time. Context information is added for water scarcity and availability categories, flowable name is applied as context for land occupation and transformation categories. Context descriptions are provided in the original source for all other categories.

## FEDEFL Inventory Methods
The LCIA formatter generates life cycle inventory methods based on groups of elementary flows identified in the FEDEFL. For example, an inventory method for energy resource use represents the summation of all instances of these flows within a dataset. Where necessary unit conversions are applied to achieve a consistent indicator unit. 

## Valuation
The LCIA formatter also includes a method-agnostic approach to convert indicators (midpoint or endpoint) to monetary values.  The primary valuation is based on modified budget constraint modeling [@weidema_valuation_2009], updated to USD2014.  A disability-adjusted life year (DALY) is valued as the global average annual potential economic production per capita; the value of ecosystem damages is calculated from the ratio of global population to terrestrial surface area, and it is also validated based on environmental preservation expenditures in selected countries.  The conversions between the different ecosystem impact indicators (e.g., PDF.m2.yr and species.yr) are based on the species density calculations from ReCiPe 2008 [@goedkoop_recipe_2009].

# Applications
The LCIA methods generated by the LCIA formatter for use with the FEDEFL are hosted publicly on the FLCAC for use by LCA practitioners and researchers. These methods support life cycle assessments performed by many parties, including member agencies for the Federal LCA Commons such as U.S. EPA, U.S. DOE, USDA, DOD, and others. These methods also enable impact assessment for researchers utilizing the US Life Cycle Inventory (USLCI) Database.
LCIA methods from the LCIA formatter are also being used in the [standard format](https://github.com/USEPA/LCIAformatter/tree/documentation/format%20specs) as inputs into other tools in the open source LCA ecosystem, including [useeior](https://github.com/USEPA/useeior) and the Electricity Life Cycle Inventory ([electricitylci](https://github.com/USEPA/ElectricityLCI)).
The system was built to be flexible enough to support creating outputs for LCIA spatially-explicit characterization factors.

# Acknowledgements
The creation of this software was funded by the [SERDP-ESTCP research program](https://www.serdp-estcp.org/) under
project WP-2757, and conducted via EPA contract EP-C-16-015, Task Order 68HERC19F0292 with ERG. The authors wish to acknowledge additional support from Ashley Edelen, Danny Hage, Troy Hottle, and Catherine Birney.

# Disclaimer
The U.S. Environmental Protection Agency, through its Office of Research and Development, conducted the research described herein under an approved Quality Assurance Project Plan (K-LRTD-0031522-QP-2). It has been subjected to the Agency’s peer and administrative review and has been approved for publication as an EPA document. Mention of trade names or commercial products does not constitute endorsement or recommendation for use.

# References
