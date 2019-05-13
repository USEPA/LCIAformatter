def cell_str(sheet, row: int, col: int) -> str:
    cell = sheet.cell(row, col)
    if cell is None:
        return ""
    if cell.value is None:
        return ""
    return str(cell.value).strip()


def cell_f64(sheet, row: int, col: int) -> float:
    cell = sheet.cell(row, col)
    if cell is None:
        return 0.0
    if cell.value is None:
        return 0.0
    try:
        return float(cell.value)
    except ValueError:
        return 0.0


def cell_val(sheet, row: int, col: int):
    cell = sheet.cell(row, col)
    if cell is None:
        return None
    return cell.value
