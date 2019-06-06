import logging as log
import lciafmt

import os


def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_traci()
    lciafmt.map_flows(data, system="TRACI2.1")
    data.to_csv(outputpath+"traci_2.1.csv", index=False)
    lciafmt.to_jsonld(data, outputpath+"traci_2.1_json.zip")


if __name__ == "__main__":
    main()
