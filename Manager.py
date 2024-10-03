import time
from datetime import datetime as dt

from items import Post
from settings import settings
from logger.logger import Logger
from util.database import Database
from util.garbage_collector import tmp_recycler
from util.utils import convert_to_mp4, get_filename

from pytwitter.error import PyTwitterError
from dotenv import load_dotenv

load_dotenv()
logger = Logger('BotsManager')
db = Database(settings['POSTS_DATABASE'])


def manager(account_username: str, post: Post) -> bool:
    automated_user = settings['AUTOMATED_USERS'].get(account_username)
    if not automated_user:
        logger.error(f'bot with username "{account_username}" not found')
        return False

    total_minutes = round((post.upload_date - dt.now()).total_seconds() / 60)

    logger.info(f'scheduling a tweet to post to username "{account_username}" after {f"{total_minutes} minutes" if total_minutes < 60 else f"{total_minutes/60} hours"}')
    time.sleep(total_minutes * 60)

    if post.post_type == 'video':
        if post.media_file_path.split('.')[0] != '.mp4':
            logger.debug(f'converting video file: "{get_filename(post.media_file_path)}" to mp4 extension')
            post.media_file_path = convert_to_mp4(post.media_file_path)

    logger.info(f'making a post with bot username: "{account_username}"')
    automated_user = automated_user()
    try: uploaded_post = automated_user.post(post)
    except PyTwitterError as e:
        logger.error(f'failed to make a post on page username: "{account_username}" error: "{e}"')
        return False

    if uploaded_post:
        db.insert_tweet(tuple(value[-1] for value in post.items()))
        db.delete_record(post.index, 'posts')

        logger.info(f'post index_id: "{post.index}" was successfully posted on page username "{account_username}" and deleted from database table "posts"')
        if post.media_file_path: tmp_recycler(post.media_file_path)
        return True

    logger.error(f'failed to tweet post index_id: "{post.index}" on page username "{account_username}"')
    return False


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
