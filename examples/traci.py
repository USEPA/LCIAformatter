import logging as log
import lciafmt

outputpath = '../lcia_formatter_output/'

def main():
    log.basicConfig(level=log.INFO)
    data = lciafmt.get_traci()
    lciafmt.map_flows(data, system="TRACI2.1")
    data.to_csv(outputpath+"traci_2.1.csv", index=False)
    lciafmt.to_jsonld(data, outputpath+"traci_2.1_json.zip")


if __name__ == "__main__":
    main()
