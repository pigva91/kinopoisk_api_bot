from telebot.handler_backends import State, StatesGroup


class SearchMovie(StatesGroup):
    number_of_results = State()
    movie_name = State()
    min_rating = State()
    max_rating = State()
    rating_sort_order = State()
    waiting_for_date_input = State()
    results_per_page = State()
    sort_by_rating_count = State()
    paginator = State()
