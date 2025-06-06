from .google_sheets import GoogleSheetsManager
from .convert_functions import convert_pricing, convert_room_capacities, RoomCapacity
import math
from datetime import datetime, timedelta


class PricingMessage:
    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message


class PriceCalculator:

    INPUT_ERROR = "Неверный ввод"
    TOO_MANY_GUESTS = "Слишком много гостей"
    SUCCESS = "Успех"
    GUESTS_LIMIT = 15

    def __init__(self, google_sheets_manager: GoogleSheetsManager):
        self.google_sheets_manager = google_sheets_manager
    
    
    async def find_best_room(self, adults: int, children: int, possible_rooms: list[RoomCapacity]):
        max_capacity = max(room.capacity for room in possible_rooms)
        if max_capacity < adults + children:
            return self.TOO_MANY_GUESTS
        elif adults + children < 2:
            if adults + children <= 0:
                return self.INPUT_ERROR
            else:
                return list(sorted(possible_rooms, key=lambda x: x.capacity))[0]
        else:
            for room in possible_rooms:
                if room.capacity == adults + children:
                    return room
            return self.INPUT_ERROR

    
    async def get_possible_rooms(self, adults: int, children: int):
        sheets = await self.google_sheets_manager.get_all_sheets()
        rooms_with_capacities = list()
        for sheet in sheets:
            room = await self.google_sheets_manager.get_sheet_data(sheet, convert_room_capacities)
            rooms_with_capacities.append(room)
        return rooms_with_capacities


    async def calculate_best_price(self, start_date: str, end_date: str, adults: int, children: int):
        possible_rooms = await self.get_possible_rooms(adults, children)
        best_room = await self.find_best_room(adults, children, possible_rooms)
        if best_room == PriceCalculator.TOO_MANY_GUESTS:
            max_capacity = max(room.capacity for room in possible_rooms)
            return PricingMessage(best_room, "Похоже, мы не сможем заселить всех гостей в один номер. Опишите, пожалуйста, схему размещения гостей по номерам в формате:\n\n**кол-во гостей в первом номере** + **кол-во гостей во втором номере** + ...\n\n**Обратите внимание: максимальное количество гостей в одном номере - " + str(max_capacity) + "**")
        elif best_room == PriceCalculator.INPUT_ERROR:
            return PricingMessage(best_room, "Не совсем понял вас - давайте попробуем еще раз :)")
        else:
            pricing_list = await self.google_sheets_manager.get_sheet_data(best_room.sheet_name, convert_pricing)
            total_sum = 0
            start_date, end_date = datetime.strptime(start_date, "%d.%m"), datetime.strptime(end_date, "%d.%m")
            current = start_date
            while current < end_date:
                total_sum += pricing_list.get_price(current, True) * adults + pricing_list.get_price(current, False) * children
                current += timedelta(days=1)
            return PricingMessage(
                    self.SUCCESS,
                    (
                        f"📅 {(end_date - start_date).days} ночей\n\n"
                        + f"👨 {adults} взрослых"
                        + (f" + 👧 {children} детей" if children > 0 else "")
                        + "\n\n"
                        + "🍽 Питание включено\n\n"
                        + f"💰 Стоимость: от {int(total_sum)}₽"
                    )
                )
