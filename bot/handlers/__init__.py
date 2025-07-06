from aiogram import Dispatcher
from . import start  # добавь сюда другие модули по мере роста

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
