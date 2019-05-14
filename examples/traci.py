import logging as log
import lciafmt


def main():
    log.basicConfig(level=log.INFO)
    data = lciafmt.get_traci()
    lciafmt.map_flows(data, system="TRI")
    data.to_csv("../out/traci_2.1.csv", index=False)
    # lciafmt.to_jsonld(data, "../out/traci_2.1_json.zip")


if __name__ == "__main__":
    main()
