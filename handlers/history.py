from loader import bot
from telebot.types import Message
from API.site_api import format_movie_info
from states.movies_information import SearchMovie
from keyboards.reply.buttons import get_main_menu_keyboard
from database.model import History, User
from datetime import datetime
from typing import List


@bot.message_handler(commands=["history"])
@bot.message_handler(func=lambda message: message.text == "История поиска")
def command_history(message: Message) -> None:
    """Обработчик команды /history и сообщения "История поиска".
    Запрашивает у пользователя дату поиска в формате YYYY-MM-DD.
    :param message: Входящее сообщение от пользователя.
    :return: None
    """
    bot.send_message(
        message.from_user.id, "Пожалуйста, введите дату поиска в формате YYYY-MM-DD."
    )
    bot.set_state(
        message.from_user.id, SearchMovie.waiting_for_date_input, message.chat.id
    )


@bot.message_handler(
    state=SearchMovie.waiting_for_date_input, regexp=r"^\d{4}-\d{2}-\d{2}$"
)
def get_date(message: Message) -> None:
    """Обработчик ввода даты пользователем.
    Проверяет введенную дату и отображает историю поиска пользователя для заданной даты.
    :param message: Входящее сообщение от пользователя.
    :return: None
    """
    wait_message = bot.send_message(message.from_user.id, "Пожалуйста, подождите...")
    date = parse_date(message.text, message.from_user.id)
    if not date:
        bot.delete_message(message.chat.id, wait_message.message_id)
        return
    bot.delete_message(message.chat.id, wait_message.message_id)

    user, created = User.get_or_create(user_id=message.from_user.id)
    histories = fetch_user_histories(user, date)

    if not histories:
        bot.send_message(message.from_user.id, "У вас нет истории поиска на эту дату.")
        return

    history_text = format_history(histories)

    if len(history_text) > 4096:
        send_long_message(message.from_user.id, history_text)
    else:
        bot.send_message(
            message.from_user.id, history_text, reply_markup=get_main_menu_keyboard()
        )

    bot.delete_state(message.from_user.id, message.chat.id)


def parse_date(date_str: str, user_id: int) -> datetime:
    """Проверяет входящую дату.
    :param date_str: Строка даты в формате YYYY-MM-DD.
    :param user_id: ID пользователя.
    :return: Объект datetime.
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date > datetime.now():
            bot.send_message(user_id, "Дата не может быть в будущем.")
            return None
        return date
    except ValueError:
        bot.send_message(user_id, "Пожалуйста, введите дату в формате YYYY-MM-DD.")
        return None


def fetch_user_histories(user: User, date: datetime) -> List[History]:
    """Получает историю поиска пользователя на заданную дату.
    :param user: Объект User.
    :param date: Объект datetime.
    :return: Список объектов History.
    """
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())

    return History.select().where(
        History.user == user,
        (History.timestamp >= start_time) & (History.timestamp <= end_time),
    )


def format_history(histories: List[History]) -> str:
    """Форматирует историю поиска для вывода.
    :param histories: Список объектов History.
    :return: Строка с форматированной историей поиска.
    """
    history_text = "История поиска:\n\n"

    for history in histories:
        movie_info = {
            "timestamp": history.timestamp,
            "user_id": history.user,
            "type": history.search_type,
            "name": history.movie_name,
            "description": history.description,
            "rating": {"kp": history.rating},
            "year": history.year,
            "genres": [{"name": genre.strip()} for genre in history.genre.split(",")],
            "ageRating": history.age_rating,
            "poster": {"url": history.poster_url},
        }

        history_info = format_movie_info(movie_info)
        _, history_text_part = history_info
        history_text_part += (
            f"\n📅Время поиска: {history.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            f"🆔ID пользователя: {history.user}\n"
            f"🔍Тип поиска: {history.search_type}\n"
        )
        history_text += (
            history_text_part + "\n_______________________________________\n"
        )
    return history_text


def send_long_message(user_id: int, history_text: str):
    """Разделяет и отправляет длинные сообщения частями."""
    parts = [history_text[i : i + 4096] for i in range(0, len(history_text), 4096)]
    for part in parts:
        bot.send_message(user_id, part, reply_markup=get_main_menu_keyboard())