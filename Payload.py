from dataclasses import dataclass


@dataclass
class Payload:
    CHECK: bool
    Product_name: str
    Note: str
    Last_Update: str
    Product_link: str
    PRODUCT_COMPARE: str
    DONGIAGIAM_MIN: float
    DONGIAGIAM_MAX: float
    DONGIA_LAMTRON: float
    IDSHEET_MIN: str
    SHEET_MIN: str
    CELL_MIN: str
    IDSHEET_MAX: str
    SHEET_MAX: str
    CELL_MAX: str
    IDSHEET_STOCK: str
    SHEET_STOCK: str
    CELL_STOCK: str
    IDSHEET_BLACKLIST: str
    SHEET_BLACKLIST: str
    CELL_BLACKLIST: str
    Price: float
    Seller: str

    def __init__(self, data):
        self.CHECK = data[0]
        self.Product_name = data[1]
        self.Note = data[2]
        self.Last_Update = data[3]
        self.Product_link = data[4]
        self.PRODUCT_COMPARE = data[5]
        self.DONGIAGIAM_MIN = data[6]
        self.DONGIAGIAM_MAX = data[7]
        self.DONGIA_LAMTRON = data[8]
        self.IDSHEET_MIN = data[9]
        self.SHEET_MIN = data[10]
        self.CELL_MIN = data[11]
        self.IDSHEET_MAX = data[12]
        self.SHEET_MAX = data[13]
        self.CELL_MAX = data[14]
        self.IDSHEET_STOCK = data[15]
        self.SHEET_STOCK = data[16]
        self.CELL_STOCK = data[17]
        self.IDSHEET_BLACKLIST = data[18]
        self.SHEET_BLACKLIST = data[19]
        self.CELL_BLACKLIST = data[20]
        self.Price = data[21]
        self.Seller = data[22]