from loader import bot
from telebot.types import Message, BotCommand, CallbackQuery
from API.site_api import (
    search_by_name,
    search_by_rating,
    send_movies_info,
    search_by_budget,
    save_history,
)
from keyboards.reply.buttons import buttons
from keyboards.inline.buttons import get_pagination_keyboard
from typing import List, Dict


DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("search_by_name", "Поиск по названию"),
    ("search_by_rating", "Поиск по рейтингу"),
    ("search_by_low_budget", "Поиск с низким бюджетом"),
    ("search_by_high_budget", "Поиск с высоким бюджетом"),
    ("history", "Просмотр истории запросов"),
)


def set_default_commands(bot) -> None:
    """Устанавливает набор команд по умолчанию для бота.
    :param bot: Телеграм бот.
    :return: None
    """
    bot.set_my_commands([BotCommand(*cmd) for cmd in DEFAULT_COMMANDS])


@bot.message_handler(commands=["start"])
def command_start_handler(message: Message) -> None:
    """Обработчик команды /start.
    :param message: Сообщение, содержащее команду /start.
    :return: None
    """
    bot.send_message(
        message.from_user.id,
        f"Добро пожаловать, {message.from_user.full_name}! Я чат-бот для поиска фильмов и сериалов на платформе "
        f"КиноПоиск. Выбери, что ты хочешь сделать!",
        reply_markup=buttons(),
    )


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda message: message.text == "Вывести справку")
def command_help_handler(message: Message) -> None:
    """Обработчик команды /help.
    :param message: Сообщение, содержащее команду /help.
    :return: None
    """
    bot.send_message(
        message.from_user.id,
        "Доступные команды:\n"
        + "\n".join([f"/{cmd[0]} - {cmd[1]}" for cmd in DEFAULT_COMMANDS]),
    )


@bot.message_handler(func=lambda message: message.text.lower() == "главное меню")
def command_back_to_menu(message: Message) -> None:
    """Обработчик команды "Главное меню".
    :param message: Сообщение, содержащее команду /back_to_menu.
    :return: None
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id, "Выбери, что ты хочешь сделать!", reply_markup=buttons()
    )


def send_movies_page(
    user_id: int, movies: List[Dict], search_type: str, page: int = 1
) -> None:
    """Отправляет пользователю страницу с фильмами.
    :param user_id: Идентификатор пользователя, для которого выполняется поиск.
    :param movies: Список фильмов, информацию о которых нужно отправить.
    :param search_type: Тип поиска, который был использован пользователем.
    :param page: Номер страницы результатов поиска.
    :return: None
    """
    send_movies_info(user_id, movies)
    if movies:
        bot.send_message(
            user_id, "Показать еще варианты?", reply_markup=get_pagination_keyboard()
        )
        save_history(user_id, movies, search_type)
    else:
        bot.send_message(user_id, "Ничего не найдено")
        bot.delete_state(user_id)


@bot.callback_query_handler(
    func=lambda callback: callback.data in ["next_page", "prev_page"]
)
def process_page_change(callback: CallbackQuery) -> None:
    """Обработчик нажатия кнопок управления страницами.
    :param callback: Объект CallbackQuery.
    :return: None
    """
    get_page_data(callback.from_user.id, callback.message.chat.id, callback.data)


def get_page_data(user_id: int, chat_id: int, page_action: str) -> None:
    """Вспомогательная функция для получения данных страницы.
    :param user_id: Идентификатор пользователя.
    :param chat_id: Идентификатор чата.
    :param page_action: Действие, которое нужно выполнить.
    :return: None
    """
    with bot.retrieve_data(user_id, chat_id) as data:
        if page_action == "next_page":
            page = data.get("current_page", 1) + 1
        elif page_action == "prev_page":
            page = max(1, data.get("current_page", 1) - 1)

        if data["search_type"] == "rating":
            movies = search_by_rating(
                user_id,
                data["count_movies"],
                data["sort_type"],
                data["rating"],
                page,
            )
        elif data["search_type"] == "name":
            movies = search_by_name(user_id, data["name"], data["count_movies"], page)

        elif data["search_type"] == "budget":
            movies = search_by_budget(
                user_id, data["count_movies"], data["sort_type"], page
            )

        data["current_page"] = page
        send_movies_page(user_id, movies, data["search_type"], page)
