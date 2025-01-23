from loader import bot
from telebot.types import Message
from API.site_api import search_by_budget
from handlers.handlers import send_movies_page
from states.movies_information import SearchMovie
from keyboards.reply.buttons import get_main_menu_keyboard


@bot.message_handler(commands=["search_by_low_budget", "search_by_high_budget"])
@bot.message_handler(
    func=lambda message: message.text
    in [
        "Поиск с низким бюджетом",
        "Поиск с высоким бюджетом",
    ]
)
def command_search_by_budget(message: Message) -> None:
    command = message.text.lower()
    bot.set_state(message.from_user.id, SearchMovie.number_of_results, message.chat.id)
    bot.send_message(
        message.from_user.id,
        "Введите количество фильмов, которые вы хотите вывести (от 1 до 100):",
        reply_markup=get_main_menu_keyboard(),
    )

    sort_command = (
        "/search_by_low_budget" if "низким" in command else "/search_by_high_budget"
    )
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["sort_command"] = sort_command


@bot.message_handler(state=SearchMovie.number_of_results)
def process_search_by_budget(message: Message) -> None:
    """"""
    if not message.text.isdigit():
        bot.send_message(
            message.from_user.id,
            "Неправильный формат. Введите целое число от 1 до 100.",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    count = int(message.text)
    if count < 1 or count > 100:
        bot.send_message(
            message.from_user.id, "Количество фильмов должно быть от 1 до 100."
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["count_movies"] = count
        data["current_page"] = 1
        sort_types = {"/search_by_low_budget": 1, "/search_by_high_budget": -1}
        data["sort_type"] = sort_types.get(data.get("sort_command"))

        if data["sort_type"] is None:
            bot.send_message(message.from_user.id, "Неверный тип сортировки.")
            return

        movies = search_by_budget(
            message.from_user.id,
            data["count_movies"],
            data["sort_type"],
        )
        data["search_type"] = "budget"
        send_movies_page(message.from_user.id, movies, data["search_type"], page=1)