from datetime import datetime


class DatePrice:
    def __init__(self, start_date: str, end_date: str, price: float):
        self.start_date = datetime.strptime(start_date, "%d.%m")
        self.end_date = datetime.strptime(end_date, "%d.%m")
        self.price = price

class RoomPricing:
    def __init__(self, room_type: str, adult_prices: list[DatePrice], child_prices: list[DatePrice]):
        self.room_type = room_type
        self.adult_prices = adult_prices
        self.child_prices = child_prices

    def get_price(self, date: datetime, is_adult: bool) -> float:
        target_prices = self.adult_prices if is_adult else self.child_prices
        for price in target_prices:
            if price.start_date <= date <= price.end_date:
                return price.price
        return 0


class RoomCapacity:
    def __init__(self, sheet_name: str, room_type: str, capacity: int):
        self.sheet_name = sheet_name
        self.room_type = room_type
        self.capacity = capacity


def convert_date_price(date: str, price: float) -> DatePrice:
    # В таблице дата начала и конца разделены символом "-"
    start_date, end_date = date.split("-")
    return DatePrice(start_date, end_date, price)


def convert_pricing(sheet_data: list[list[str]], sheet_name: str = None) -> RoomPricing:
    # На первой строке даты - запишем их в список
    dates = sheet_data[0][1:]
    # Соберем все цены для взрослых
    adult_prices = list(float(price) for price in (sheet_data[1][1:] if sheet_data[1][0] == "Взрослый" else sheet_data[2][1:]))
    # Соберем все цены для детей
    child_prices = list(float(price) for price in (sheet_data[2][1:] if sheet_data[2][0] == "Ребенок" else sheet_data[1][1:]))

    converted_adult_prices = list(convert_date_price(date, price) for date, price in zip(dates, adult_prices))
    converted_child_prices = list(convert_date_price(date, price) for date, price in zip(dates, child_prices))
    print(converted_adult_prices)
    print(converted_child_prices)

    return RoomPricing(sheet_data[0][0], converted_adult_prices, converted_child_prices)


def convert_room_capacities(sheet_data: list[list[str]], sheet_name: str = None):
    room_name = sheet_data[0][0]
    room_capacity = int(sheet_data[3][1]) if sheet_data[3][0] == "Максимально гостей" else None
    if not room_capacity:
        raise Exception("Максимально гостей не найден")
    return RoomCapacity(sheet_name, room_name, room_capacity)
