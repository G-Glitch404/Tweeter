import time
from datetime import datetime as dt

from logger.logger import Logger
from Exceptions import exceptions
from items import Post
from settings import settings
from automated_users import automated_users
from util.database import Database
from dotenv import load_dotenv

load_dotenv()
logger = Logger('BotsManager')
db = Database(settings['POSTS_DATABASE'])


def manager(account_username: str, post: Post) -> bool:
    automated_user = automated_users.get(account_username)
    if not automated_user:
        logger.error(f'bot with username "{account_username}" not found')
        raise exceptions.NoUsername(f'bot with username "{account_username}" not found')

    total_minutes = round((dt.now() - post.upload_date).total_seconds() / 60)

    logger.info(f'scheduling a tweet to post to username "{account_username}" after {f"{total_minutes} minutes" if total_minutes < 60 else f"{total_minutes/60} hours"}')
    time.sleep(total_minutes * 60)

    logger.info(f'making a post with bot username: "{account_username}"')
    automated_user = automated_user()
    if automated_user.post(post):
        db.insert_tweet(tuple(value[-1] for value in post.items()))
        db.delete_record(post.index, 'posts')

        logger.info(f'post index_id: "{post.index}" was successfully posted on page username "{account_username}" and deleted from database table "posts"')
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
