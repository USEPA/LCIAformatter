from setuptools import setup

setup(
    name="lciafmt",
    version="0.1.1",
    packages=["lciafmt"],
    install_requires=["fedelemflowlist","olca-ipc", "pandas", "xlrd"],
    dependency_links=["git+git://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List.git@v1.0.1#egg=fedelemflowlist",
                      "https://pypi.python.org/simple/",
                      "https://pypi.python.org/simple/",
                      "https://pypi.python.org/simple/"],
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
