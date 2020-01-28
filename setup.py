from setuptools import setup

setup(
    name="lciafmt",
    version="0.1.1",
    packages=["lciafmt"],
    install_requires=["fedelemflowlist @ git+git://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List@v1.0.1#egg=fedelemflowlist",
                      "olca-ipc", "pandas", "xlrd"],
    license="CC0",
    classifiers=[
        "Development Status :: Alpha",
        "Environment :: IDE",
        "Intended Audience :: Science/Research",
        "License :: CC0",
        "Programming Language :: Python :: 3.x",
        "Topic :: Utilities",
    ],
)
