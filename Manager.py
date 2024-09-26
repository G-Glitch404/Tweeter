from logger.logger import Logger
from Exceptions import exceptions
from items import Post
from settings import settings, automated_users
from util.database import Database
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')
logger = Logger('BotsManager')
db = Database(settings['POSTS_DATABASE'])


def manager(account_username: str, post: Post) -> None:
    automated_user = automated_users.get(account_username)
    if not automated_user:
        logger.error(f'bot with username "{account_username}" not found')
        raise exceptions.NoUsername(f'bot with username "{account_username}" not found')

    automated_user = automated_user()
    logger.info(f'making a post with bot username: "{account_username}"')
    automated_user.tweet(post)

    db.insert_tweet(tuple(value[-1] for value in post.items()))
    db.delete_record(post.index, 'posts')


if __name__ == '__main__':
    pass
    # TODO: Run some tests here
