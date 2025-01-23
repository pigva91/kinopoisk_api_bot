from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_pagination_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками для навигации по страницам.
    :return InlineKeyboardMarkup: Объект клавиатуры.
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="⬅️Предыдущая страница", callback_data="prev_page"),
        InlineKeyboardButton(text="➡️Следующая страница", callback_data="next_page"),
    )
    return keyboard