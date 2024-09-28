import logging
from util.utils import path

settings = {
    "LOGGING_LEVEL": logging.DEBUG,
    "PROXIES": None,
    "POSTS_DATABASE": path('.db', 'posts.db'),
    "RECON_SUBREDDITS": ['NoahGetTheBoat'],
}
