import pandas as pd
import lciafmt
from lciafmt.util import store_method, save_json, log, drop_county_data


method = lciafmt.Method.TRACI2_2
regions = ['states', 'countries']

def main():

    df = lciafmt.get_method(method)
    mapping = method.get_metadata()['mapping']
    mapped_df = lciafmt.map_flows(df, system=mapping)

    # write the result to parquet, includes states and counties as FIPS,
    # and all countries
    store_method(mapped_df, method)

    # drop county FIPS, leave only US states and countries
    all_df = drop_county_data(mapped_df)

    save_json(method, all_df, name='TRACI2.2', regions=regions)

if __name__ == "__main__":
    main()
    mapped_df = lciafmt.get_mapped_method(method)
