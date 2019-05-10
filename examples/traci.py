import logging as log
import lciafmt


def main():
    log.basicConfig(level=log.INFO)
    data = lciafmt.get_traci()
    data.to_csv("../out/traci.csv")

if __name__ == "__main__":
    main()
