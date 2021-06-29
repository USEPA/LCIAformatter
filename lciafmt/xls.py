# xls.py (lciafmt)
# !/usr/bin/env python3
# coding=utf-8
"""
Functions to support reading Microsoft Excel files for lciafmt
"""

import openpyxl


def cell_str(sheet: openpyxl.worksheet.worksheet.Worksheet,
             row: int, col: int) -> str:
    v = cell_val(sheet, row, col)
    if v is None:
        return ""
    return str(v).strip()


def cell_f64(sheet: openpyxl.worksheet.worksheet.Worksheet,
             row: int, col: int) -> float:
    v = cell_val(sheet, row, col)
    if v is None:
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0


def cell_val(sheet: openpyxl.worksheet.worksheet.Worksheet,
             row: int, col: int):
    if row < 0 or row >= sheet.max_row:
        return None
    if col < 0 or col >= sheet.max_column:
        return None
    cell = sheet.cell(row, col).value
    if cell is None:
        return None
    #checks for errortype N/A and returns None
    #if cell.ctype == 5:
    #    return None
    return cell


def cell_empty(sheet: openpyxl.worksheet.worksheet.Worksheet,
               row: int, col: int) -> bool:
    v = cell_val(sheet, row, col)
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    return False


def iter_cells(sheet: openpyxl.worksheet.worksheet.Worksheet):
    for row in range(0, sheet.max_row):
        for col in range(0, sheet.max_column):
            yield row, col
