import logging
from util.utils import path
from Bots.DailyComic import Bot as DailyComic

automated_users = {
    "NewDayNewComic": DailyComic
}

settings = {
    "LOGGING_LEVEL": logging.DEBUG,
    "PROXIES": None,
    "POSTS_DATABASE": path('.db', 'posts.db'),
}
