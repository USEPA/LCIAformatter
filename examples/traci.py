import logging as log
import lciafmt


def main():
    log.basicConfig(level=log.INFO)
    lciafmt.get_traci()


if __name__ == "__main__":
    main()
