import logging
from loader import bot
from telebot.custom_filters import StateFilter
from handlers.handlers import set_default_commands
from handlers.search_by_budget import command_search_by_budget
from handlers.search_by_name import command_search_by_name
from handlers.search_by_rating import command_search_by_rating
from handlers.history import command_history
from database.model import db


logging.basicConfig(level=logging.INFO)
logging.info("Запуск бота")

if __name__ == "__main__":
    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
