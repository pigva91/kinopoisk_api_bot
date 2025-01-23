import logging
from loader import bot
from config_data.config import settings
from database.model import User, History
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests


logging.basicConfig(level=logging.INFO)


base_params: Dict[str, Any] = {
    "token": settings.API_KEY.get_secret_value(),
    "selectFields": [
        "name",
        "description",
        "year",
        "genres",
        "rating",
        "ageRating",
        "budget",
        "poster",
    ],
    "notNullFields": [
        "name",
        "year",
        "description",
        "rating.kp",
        "genres.name",
        "ageRating",
        "budget.value",
        "poster.url",
    ],
}


def search_by_budget(
    user_id: int, count: int, sort_type: int, page: int = 1
) -> Optional[List[Dict]]:
    """Выполняет поиск фильмов по бюджету.
    :param user_id: Идентификатор пользователя, для которого выполняется поиск.
    :param count: Количество фильмов, которое нужно получить.
    :param sort_type: Тип сортировки результатов поиска.
    :param page: Номер страницы результатов поиска. По умолчанию 1.
    :return Optional[Any[Dict]]: Список фильмов, найденных по бюджету.
    """
    params = {
        **base_params,
        "sortField": "budget.value",
        "budget.value": "10000-10e20",
        "rating.kp": "1-10",
        "sortType": sort_type,
        "limit": count,
        "page": page,
    }
    movies = make_request(settings.API_URL, params, user_id)
    return movies


def search_by_name(
    user_id: int, name: str, count: int = 10, page: int = 1
) -> Optional[List[Dict]]:
    """Выполняет поиск фильмов по названию.
    :param user_id: Идентификатор пользователя, для которого выполняется поиск.
    :param name: Название фильма.
    :param count: Количество фильмов, которое нужно получить. По умолчанию 10.
    :param page: Номер страницы результатов поиска. По умолчанию 1.
    :return Optional[Any[Dict]]: Список фильмов, найденных по названию.
    """
    params = {
        **base_params,
        "query": name,
        "limit": count,
        "page": page,
    }
    movies = make_request(settings.API_URL + "/search", params, user_id)
    filtered_movies = [
        movie for movie in movies if name.lower() in movie["name"].lower()
    ]
    return filtered_movies[:count]


def search_by_rating(
    user_id: int, count: int, sort_type: int, rating: str, page: int = 1
) -> Optional[List[Dict]]:
    """Выполняет поиск фильмов по рейтингу.
    :param user_id: Идентификатор пользователя, для которого выполняется поиск.
    :param count: Количество фильмов, которое нужно получить.
    :param sort_type: Тип сортировки результатов поиска.
    :param rating: Диапазон рейтинга, который нужно использовать для поиска.
    :param page: Номер страницы результатов поиска. По умолчанию 1.
    :return Optional[Any[Dict]]: Список фильмов, найденных по рейтингу.
    """
    params = {
        **base_params,
        "rating.kp": rating,
        "sortField": "rating.kp",
        "sortType": sort_type,
        "limit": count,
        "page": page,
    }
    movies = make_request(settings.API_URL, params, user_id)
    return movies


def save_history(user_id: int, movies: List, search_type: str) -> None:
    """Сохраняет историю поиска фильмов в БД.
    :param user_id: Идентификатор пользователя, который выполнил поиск.
    :param movies: Список фильмов, которые были найдены.
    :param search_type: Тип поиска, который был использован пользователем.
    :return None
    """
    user, _ = User.get_or_create(user_id=user_id)

    for movie in movies:
        if not movie.get("name") or movie is None:
            continue

        poster_url = movie.get("poster")
        if poster_url is not None:
            poster_url = poster_url.get("url", "Нет постера")

        History.create(
            user=user,
            movie_name=movie.get("name"),
            description=movie.get("description"),
            rating=movie.get("rating", {}).get("kp"),
            year=movie.get("year"),
            genre=", ".join(genre["name"] for genre in movie.get("genres", [])),
            age_rating=movie.get("ageRating", "Нет рейтинга"),
            poster_url=poster_url,
            timestamp=datetime.now(),
            search_type=search_type,
        )


def format_movie_info(movie: Dict) -> tuple:
    """Форматирует информацию о фильме для отправки пользователю.
    :param movie: Словарь с информацией о фильме.
    # :param show_history: Флаг, указывающий, нужно ли показывать историю поиска.
    :return tuple: Кортеж, содержащий URL постера фильма и отформатированную информацию о фильме.
    """
    genres = movie.get("genres", [])
    budget = movie.get("budget", {}).get("value", "Нет данных")
    currency = movie.get("budget", {}).get("currency", "")
    poster_url = movie.get("poster").get("url", "Нет постера")

    caption_parts = [
        f"📽Название: {movie['name']}\n"
        f"🎯Жанр: {', '.join(genre['name'] for genre in genres) or 'Нет жанра'}\n"
        f"💯Рейтинг: {movie.get('rating', {}).get('kp')}\n"
        f"🗓️Год выпуска: {movie.get('year')}\n"
        f"🔞Возрастной рейтинг: {'Нет рейтинга' if movie.get('ageRating') is None else f'{movie.get('ageRating')}+'}\n"
        f"💰Бюджет: {budget} {currency}\n"
        f"🎬Описание: {'Нет описания' if not movie.get('description') else movie.get('description')}\n"
    ]

    caption = "\n".join(caption_parts)
    return poster_url, caption[:1024] if len(caption) > 1024 else caption


def send_movies_info(chat_id: int, movies: Dict[str, Any]) -> None:
    """Отправляет информацию о фильмах пользователю в виде сообщений с фотографиями.
    :param chat_id: Идентификатор чата, в который нужно отправить информацию о фильмах.
    :param movies: Список фильмов, информацию о которых нужно отправить.
    :return None
    """
    valid_movies = []
    for movie in movies:
        if not movie.get("name"):
            logging.info(f"Фильм {movie.get('id')} не имеет названия.")
        else:
            valid_movies.append(movie)

    for movie in valid_movies:
        poster_url, caption = format_movie_info(movie)

        if poster_url:
            bot.send_photo(chat_id, poster_url, caption)
        else:
            bot.send_message(chat_id, caption + "🖼Постер: Нет постера\n\n")


def make_request(
    url: str, params: Dict[str, Any], user_id: int
) -> List[Dict[str, Any]]:
    """Выполняет HTTP-запрос к указанному URL с заданными параметрами и возвращает результат в виде JSON.
    :param url: URL, к которому нужно выполнить запрос.
    :param params: Параметры, которые нужно передать в запросе.
    :param user_id: Идентификатор пользователя, для которого выполняется запрос.
    :return List[Dict[str, Any]]: Результат запроса в виде списка словарей, если запрос был успешным, None в противном
    случае.
    """
    response = requests.get(url, params=params)

    try:
        response.raise_for_status()
        return response.json().get("docs", [])
    except (requests.HTTPError, requests.RequestException) as err:
        logging.error(
            f"Произошла ошибка при запросе '{url}' с параметрами '{params}' для пользователя {user_id}: {err}."
        )
        return []