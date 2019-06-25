import logging as log
import os

import lciafmt


def main():
    modulepath = os.path.dirname(
        os.path.realpath(__file__)).replace('\\', '/')
    outputpath = modulepath + '/../output/'
    os.makedirs(outputpath, exist_ok=True)

    log.basicConfig(level=log.INFO)
    data = lciafmt.get_method(lciafmt.Method.RECIPE_2016)
    data.to_csv(outputpath + "recipe_2016.csv", index=False)


if __name__ == "__main__":
    main()
