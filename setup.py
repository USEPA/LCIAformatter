from setuptools import setup

setup(
    name="lciafmt",
    version="1.0.5",
    packages=["lciafmt"],
    package_dir={'lciafmt': 'lciafmt'},
    package_data={'lciafmt': ["data/*.*"]},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=["fedelemflowlist @ git+https://github.com/USEPA/Federal-LCA-Commons-Elementary-Flow-List.git#egg=fedelemflowlist",
                      "esupy @ git+https://github.com/USEPA/esupy.git#egg=esupy",
                      "olca-ipc==0.0.12",
                      "pandas>=0.22",
                      "openpyxl>=3.0.7",
                      "pyyaml>=5.3"
                      ],
    extras_require={"ImpactWorld": ["pyodbc >= 4.0.30;platform_system=='Windows'"]},
    license="MIT",
    author='Ben Young, Michael Srocka, Wesley Ingwersen, Troy Hottle, Ben Morelli',
    author_email='ingwersen.wesley@epa.gov',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: IDE",
        "Intended Audience :: Science/Research",
        "License :: MIT",
        "Programming Language :: Python :: 3.x",
        "Topic :: Utilities",
    ],
    description='Standardizes the format and flows of life cycle impact assessment data'
)
