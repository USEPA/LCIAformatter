from setuptools import setup

setup(
    name="lcia_formatter",
    version="0.1",
    packages=["lciafmt"],
    install_requires=["olca-ipc", "pandas"],
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
