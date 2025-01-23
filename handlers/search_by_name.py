from loader import bot
from telebot.types import Message
from API.site_api import search_by_name
from handlers.handlers import send_movies_page
from states.movies_information import SearchMovie
from keyboards.reply.buttons import get_main_menu_keyboard


@bot.message_handler(commands=["search_by_name"])
@bot.message_handler(func=lambda message: message.text == "Поиск по названию")
def command_search_by_name(message: Message):
    """Обработчик команды поиска фильма по названию.
    :param message: Сообщение с командой поиска фильма по названию.
    :return: None
    """
    bot.send_message(
        message.from_user.id,
        "Введите название фильма или сериала, который вы хотите найти:",
        reply_markup=get_main_menu_keyboard(),
    )
    bot.set_state(message.from_user.id, SearchMovie.movie_name, message.chat.id)


@bot.message_handler(state=SearchMovie.movie_name)
def process_search_by_name(message: Message) -> None:
    """Обработчик ввода названия фильма для поиска.
    :param message: Сообщение с названием фильма.
    :return: None
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"] = message.text
    movies = search_by_name(message.from_user.id, data["name"])
    if not movies:
        bot.send_message(
            message.from_user.id,
            f"Извините, фильм '{data['name']}' не найден",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    bot.send_message(
        message.from_user.id,
        "Сколько результатов вывести на экран?",
        reply_markup=get_main_menu_keyboard(),
    )
    bot.set_state(message.from_user.id, SearchMovie.results_per_page, message.chat.id)


@bot.message_handler(state=SearchMovie.results_per_page)
def process_search_by_name_count(message: Message) -> None:
    """Обработчик ввода количества результатов поиска.
    :param message: Сообщение с количеством результатов поиска.
    :return: None
    """
    if not message.text.isdigit():
        bot.send_message(
            message.from_user.id,
            "Пожалуйста, введите целое число от 0 до 100.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    count = int(message.text)
    if count < 1 or count > 100:
        bot.send_message(
            message.from_user.id,
            "Значение должно быть от 1 до 100.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["count_movies"] = count
        data["current_page"] = 1
        movies = search_by_name(
            message.from_user.id, data["name"], data["count_movies"]
        )
        data["search_type"] = "name"
        send_movies_page(message.from_user.id, movies, data["search_type"], page=1)