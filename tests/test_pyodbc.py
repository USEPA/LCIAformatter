"""Test for the presence of pyodbc + MS Access driver."""

import logging
import sys

import pytest

logger = logging.getLogger(__name__)


# @pytest.mark.skipif(sys.platform != "win32", reason="PYDOBC only on windows")
@pytest.mark(reason="Driver temporarily not available on action see issue #85")
def test_find_pyodbc_driver():
    """In wind32 platform, pyodbc must be installed, with MS Access drivers."""
    try:
        import pyodbc  # pylint: disable=C0415
    except ImportError:
        logger.error(
            """Must install pyodbc for ImpactWorld."""
            """See install instructions for optional package"""
            """installation or install it independently and retry."""
        )
        raise
    driver_check = list(pyodbc.drivers())
    driver_found = any("Microsoft Access Driver" in word for word in driver_check)
    logger.debug("Found pyodbc drivers: %s", driver_check)
    assert driver_found is True
