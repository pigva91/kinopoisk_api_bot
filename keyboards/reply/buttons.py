from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def buttons() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопками для главного меню.
    :return ReplyKeyboardMarkup: Объект клавиатуры."""
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboards.row(
        KeyboardButton(text="Вывести справку"),
        KeyboardButton(text="История поиска"),
    ),
    keyboards.row(
        KeyboardButton(text="Поиск по названию"),
        KeyboardButton(text="Поиск по рейтингу"),
    ),
    keyboards.row(
        KeyboardButton(text="Поиск с низким бюджетом"),
        KeyboardButton(text="Поиск с высоким бюджетом"),
    )
    return keyboards


def get_main_menu_keyboard():
    """Создает клавиатуру с кнопкой "Главное меню".
    :return ReplyKeyboardMarkup: Объект клавиатуры."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(text="Главное меню"))
    return keyboard


def buttons_rating_numbers() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопками для выбора рейтинга.
    :return ReplyKeyboardMarkup: Объект клавиатуры."""
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(1, 11, 5):
        keyboards.row(*[KeyboardButton(text=str(j)) for j in range(i, i + 5)])
    keyboards.row(KeyboardButton(text="Главное меню"))
    return keyboards


def filter_rating() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопками для выбора направления сортировки рейтинга.
    :return ReplyKeyboardMarkup: Объект клавиатуры."""
    keyboards = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboards.row(KeyboardButton(text="Min -> Max"), KeyboardButton(text="Max -> Min"))
    keyboards.row(KeyboardButton(text="Главное меню"))
    return keyboards
