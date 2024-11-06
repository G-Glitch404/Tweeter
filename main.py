import datetime
import time

from items import Post
from Manager import manager
from settings import settings
from util.database import Database
from util.decorators import catch_exceptions
from logger.logger import Logger
from multiprocessing import Process

logger = Logger('Control')
db = Database(settings['POSTS_DATABASE'])


@catch_exceptions
def main() -> None:
    process_index: list[tuple] = []
    while True:
        for post in db.fetch_all():
            if post[0] not in tuple(map(lambda x: x[-1], process_index)):
                logger.info(f'processing and scheduling a post with index_id: "{post[0]}" for bot username "{post[1]}"')

                if ':' not in post[4]: post[4] += ' 00:00:00'
                post[4] = datetime.datetime.strptime(post[4], '%Y-%m-%d %H:%M:%S')
                post = Post(*post)

                process = Process(target=manager, args=(post.bot_username, post))
                process.start()

                process_index.append((process, post.index))

        for process, index in process_index:
            if not process.is_alive():
                process_index.pop(process_index.index((process, index)))

        time.sleep(60)


if __name__ == '__main__':
    main()
