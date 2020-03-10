import xlrd


def cell_str(sheet: xlrd.book.sheet, row: int, col: int) -> str:
    v = cell_val(sheet, row, col)
    if v is None:
        return ""
    return str(v).strip()


def cell_f64(sheet: xlrd.book.sheet, row: int, col: int) -> float:
    v = cell_val(sheet, row, col)
    if v is None:
        return 0.0
    try:
        return float(v)
    except ValueError:
        return 0.0


def cell_val(sheet: xlrd.book.sheet, row: int, col: int):
    if row < 0 or row >= sheet.nrows:
        return None
    if col < 0 or col >= sheet.ncols:
        return None
    cell = sheet.cell(row, col)
    if cell is None:
        return None
    #checks for errortype N/A and returns None
    if cell.ctype == 5:
        return None
    return cell.value


def cell_empty(sheet: xlrd.book.sheet, row: int, col: int) -> bool:
    v = cell_val(sheet, row, col)
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    return False


def iter_cells(sheet: xlrd.book.sheet):
    for row in range(0, sheet.nrows):
        for col in range(0, sheet.ncols):
            yield row, col
