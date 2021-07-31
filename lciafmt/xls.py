# xls.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to support reading Microsoft Excel files for lciafmt
"""

import openpyxl


def cell_str(cell: openpyxl.worksheet.worksheet.Worksheet.cell) -> str:
    v = cell.value
    if v is None:
        return ""
    return str(v).strip()


def cell_f64(cell: openpyxl.worksheet.worksheet.Worksheet.cell) -> float:
    v = cell.value
    if v is None:
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0

