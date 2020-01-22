from setuptools import setup

setup(
    name="lciafmt",
    version="0.1.1",
    packages=["lciafmt"],
    install_requires=["fedelemflowlist","olca-ipc", "pandas", "xlrd"],
    dependency_links=["https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List/archive/v1.0.1.tar.gz"],
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
