from loader import bot
from telebot.types import Message
from API.site_api import search_by_rating
from handlers.handlers import send_movies_page
from states.movies_information import SearchMovie
from keyboards.reply.buttons import (
    buttons_rating_numbers,
    filter_rating,
    get_main_menu_keyboard,
)
from typing import Optional, Any


def validate_and_verify_rating(message: Message) -> Optional[Any]:
    """Валидирует и проверяет ввод рейтинга.
    :param message: Сообщение, содержащее ввод рейтинга от пользователя.
    :return: Возвращает значение рейтинга, если введено корректно, иначе None.
    """
    rating = message.text
    if not rating.isdigit() or int(rating) not in range(1, 11):
        bot.send_message(
            message.from_user.id,
            "Некорректный ввод рейтинга. Значение рейтинга должно быть от 1 до 10.",
        )
        return None
    return int(rating)


@bot.message_handler(commands=["search_by_rating"])
@bot.message_handler(func=lambda message: message.text == "Поиск по рейтингу")
def command_search_by_rating(message: Message):
    """Начало поиска фильмов по рейтингу.
    :param message: Сообщение, содержащее команду "Поиск по рейтингу".
    :return: None
    """
    bot.send_message(
        message.from_user.id,
        "Пожалуйста, введите минимальное значение рейтинга (от 1 до 10), чтобы начать поиск фильмов по рейтингу:",
        reply_markup=buttons_rating_numbers(),
    )
    bot.set_state(message.from_user.id, SearchMovie.min_rating, message.chat.id)


@bot.message_handler(state=SearchMovie.min_rating)
def process_min_rating(message: Message) -> None:
    """Обработчик ввода минимального значения рейтинга.
    :param message: Сообщение, содержащее минимальное значение рейтинга.
    :return: None
    """
    min_rating = validate_and_verify_rating(message)
    if min_rating is None:
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["min_rating"] = min_rating

        bot.send_message(
            message.from_user.id,
            "Пожалуйста, введите максимальное значение рейтинга (от 1 до 10):",
            reply_markup=buttons_rating_numbers(),
        )
        bot.set_state(message.from_user.id, SearchMovie.max_rating, message.chat.id)


@bot.message_handler(state=SearchMovie.max_rating)
def process_max_rating(message: Message) -> None:
    """Обработчик ввода максимального значения рейтинга.
    :param message: Сообщение, содержащее максимальное значение рейтинга.
    :return: None
    """
    max_rating = validate_and_verify_rating(message)
    if max_rating is None:
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["max_rating"] = max_rating

    if data["max_rating"] <= data["min_rating"]:
        bot.send_message(
            message.from_user.id,
            "Максимальное значение рейтинга должно быть больше минимального значения. "
            "Пожалуйста, введите минимальный и максимальный рейтинг заново.",
        )
        bot.set_state(message.from_user.id, SearchMovie.min_rating, message.chat.id)
        bot.send_message(
            message.from_user.id,
            "Пожалуйста, введите минимальное значение рейтинга (от 1 до 10), чтобы начать поиск фильмов по рейтингу:",
            reply_markup=buttons_rating_numbers(),
        )
        return

    bot.set_state(message.from_user.id, SearchMovie.rating_sort_order, message.chat.id)
    bot.send_message(
        message.from_user.id,
        "Пожалуйста, выберите сортировку рейтинга:",
        reply_markup=filter_rating(),
    )


@bot.message_handler(state=SearchMovie.rating_sort_order)
def process_filter_rating(message: Message) -> None:
    """Обработчик ввода значения сортировки рейтинга.
    :param message: Сообщение, содержащее значение сортировки рейтинга.
    :return: None
    """
    if message.text.lower() not in ["min -> max", "max -> min"]:
        bot.send_message(
            message.from_user.id,
            "Пожалуйста, выберите значение из предложенных кнопок.",
            reply_markup=filter_rating(),
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["sort_type"] = -1 if message.text.lower() == "max -> min" else 1

        bot.send_message(
            message.from_user.id,
            "Сколько результатов вывести на экран?",
            reply_markup=get_main_menu_keyboard(),
        )
        bot.set_state(
            message.from_user.id, SearchMovie.sort_by_rating_count, message.chat.id
        )


@bot.message_handler(state=SearchMovie.sort_by_rating_count)
def process_search_by_rating_count(message: Message) -> None:
    """Обработчик ввода количества результатов поиска.
    :param message: Сообщение, содержащее количество результатов поиска.
    :return: None
    """
    if not message.text.isdigit():
        bot.send_message(
            message.from_user.id,
            "Пожалуйста, введите число для количества результатов",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    count = int(message.text)
    if count < 1 or count > 100:
        bot.send_message(
            message.from_user.id,
            "Значение должно быть от 1 до 100",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["count_movies"] = count
        data["current_page"] = 1
        data["rating"] = f"{data['min_rating']} - {data['max_rating']}"

        movies = search_by_rating(
            message.from_user.id,
            data["count_movies"],
            data["sort_type"],
            data["rating"],
        )
        data["search_type"] = "rating"
        send_movies_page(message.from_user.id, movies, data["search_type"], page=1)