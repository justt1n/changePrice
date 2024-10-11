from dataclasses import dataclass

@dataclass
class Payload:
    CHECK: bool = False
    Product_name: str = ''
    Note: str = ''
    Last_Update: str = ''
    Product_link: str = ''
    PRODUCT_COMPARE: str = ''
    DONGIAGIAM_MIN: float = 0.0
    DONGIAGIAM_MAX: float = 0.0
    DONGIA_LAMTRON: float = 0.0
    IDSHEET_MIN: str = ''
    SHEET_MIN: str = ''
    CELL_MIN: str = ''
    IDSHEET_MAX: str = ''
    SHEET_MAX: str = ''
    CELL_MAX: str = ''
    IDSHEET_STOCK: str = ''
    SHEET_STOCK: str = ''
    CELL_STOCK: str = ''
    IDSHEET_BLACKLIST: str = ''
    SHEET_BLACKLIST: str = ''
    CELL_BLACKLIST: str = ''
    Price: float = 0.0
    Seller: str = ''

    def __init__(self, data=None):
        if data is None:
            self.CHECK = False
            self.Product_name = ''
            self.Note = ''
            self.Last_Update = ''
            self.Product_link = ''
            self.PRODUCT_COMPARE = ''
            self.DONGIAGIAM_MIN = 0.0
            self.DONGIAGIAM_MAX = 0.0
            self.DONGIA_LAMTRON = 0.0
            self.IDSHEET_MIN = ''
            self.SHEET_MIN = ''
            self.CELL_MIN = ''
            self.IDSHEET_MAX = ''
            self.SHEET_MAX = ''
            self.CELL_MAX = ''
            self.IDSHEET_STOCK = ''
            self.SHEET_STOCK = ''
            self.CELL_STOCK = ''
            self.IDSHEET_BLACKLIST = ''
            self.SHEET_BLACKLIST = ''
            self.CELL_BLACKLIST = ''
            self.Price = 0.0
            self.Seller = ''
        else:
            self.CHECK = data[0] if len(data) > 0 else False
            self.Product_name = data[1] if len(data) > 1 else ''
            self.Note = data[2] if len(data) > 2 else ''
            self.Last_Update = data[3] if len(data) > 3 else ''
            self.Product_link = data[4] if len(data) > 4 else ''
            self.PRODUCT_COMPARE = data[5] if len(data) > 5 else ''
            self.DONGIAGIAM_MIN = data[6] if len(data) > 6 else 0.0
            self.DONGIAGIAM_MAX = data[7] if len(data) > 7 else 0.0
            self.DONGIA_LAMTRON = data[8] if len(data) > 8 else 0.0
            self.IDSHEET_MIN = data[9] if len(data) > 9 else ''
            self.SHEET_MIN = data[10] if len(data) > 10 else ''
            self.CELL_MIN = data[11] if len(data) > 11 else ''
            self.IDSHEET_MAX = data[12] if len(data) > 12 else ''
            self.SHEET_MAX = data[13] if len(data) > 13 else ''
            self.CELL_MAX = data[14] if len(data) > 14 else ''
            self.IDSHEET_STOCK = data[15] if len(data) > 15 else ''
            self.SHEET_STOCK = data[16] if len(data) > 16 else ''
            self.CELL_STOCK = data[17] if len(data) > 17 else ''
            self.IDSHEET_BLACKLIST = data[18] if len(data) > 18 else ''
            self.SHEET_BLACKLIST = data[19] if len(data) > 19 else ''
            self.CELL_BLACKLIST = data[20] if len(data) > 20 else ''
            self.Price = data[21] if len(data) > 21 else 0.0
            self.Seller = data[22] if len(data) > 22 else ''