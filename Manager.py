import threading
from datetime import datetime as dt
from typing import Union

from items import Post
from settings import settings
from Bots.Bot import Bot
from logger.logger import Logger
from GUI.error_dialog import ErrorDialogUI

from util.database import Database
from util.garbage_collector import tmp_recycler
from util.decorators import catch_exceptions
from util.utils import convert_to_mp4, get_filename, get_available_bots, status_manager

from pytwitter.error import PyTwitterError
from dotenv import load_dotenv

load_dotenv()
logger = Logger('BotsManager')
db = Database(settings['POSTS_DATABASE'])


@catch_exceptions
def manager(account_username: str, post: Post) -> Union[threading.Timer, bool]:
    def upload_post(bot_username, _post: Post, **bot_account_info):
        logger.info(f'making a post with bot username: "{account_username}"')

        automated_user = Bot(logger_name=bot_username, **bot_account_info)
        try:
            uploaded_post = automated_user.post(_post)
        except PyTwitterError as e:
            err_: str = f'failed to make a post on page username: "{bot_username}" error: "{e}"'
            logger.error(err_)
            ErrorDialogUI(err_)
            status_manager(False, failed=1)
            return False

        if uploaded_post:
            db.insert_tweet(tuple(value[-1] for value in _post.items()))
            db.delete_record(_post.index, 'posts')
            status_manager(False, uploaded=1)

            logger.info(f'post index_id: "{_post.index}" was successfully posted on page username "{bot_username}" and deleted from database table "posts"')
            if _post.media_file_path: tmp_recycler(_post.media_file_path)
            return True

        err_: str = f'failed to tweet post index_id: "{_post.index}" on page username "{bot_username}"'
        logger.error(err_)
        ErrorDialogUI(err_)
        status_manager(False, failed=1)

        return False

    if post.post_type == 'video':
        if post.media_file_path.split('.')[0] != '.mp4':
            logger.debug(f'converting video file: "{get_filename(post.media_file_path)}" to mp4 extension')
            post.media_file_path = convert_to_mp4(post.media_file_path)

    account_info: dict = {}
    username: str = ''
    for account_dict in get_available_bots():
        user, info = tuple(account_dict.items())[0]
        if user == account_username:
            username: str = user
            account_info: dict = info
            break

    if not username or not account_info:
        err: str = f'no available bots found with username: "{account_username}"'
        logger.error(err)
        ErrorDialogUI(err + ' maybe corrupted files found, please re/create the bot first')
        return False

    total_minutes: int = round((post.upload_date - dt.now()).total_seconds() / 60)
    logger.info(f'scheduling a tweet to post to username "{account_username}" after {f"{total_minutes} minutes" if total_minutes < 60 else f"{total_minutes/60} hours"}')
    thread = threading.Timer(total_minutes * 60, lambda: upload_post(account_username, post, **account_info))
    thread.start()

    return thread


if __name__ == '__main__':
    from util.utils import path

    post_ = Post(
        index=0,
        post_type='image',
        body='this is just a test',
        media_file_path=path('media', 'test.jpeg'),
        upload_date=dt.now(),
        bot_username='NewDayNewComic'
    )

    manager(post_.bot_username, post_)
