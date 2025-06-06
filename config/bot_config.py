from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = eval(os.getenv("ADMIN_IDS"))
FAQ_STORAGE_PATH = os.getenv("FAQ_STORAGE_PATH")
DB_PATH = os.getenv("DB_PATH")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")




# следует удалить
'''BOT_TOKEN = "7269394176:AAHbtUCPD2VQg5wlB4kN-hFrIyoLpojyplU"
ADMIN_IDS = {429618569, 739758783}
FAQ_STORAGE_PATH = "storage/faq.json"'''
