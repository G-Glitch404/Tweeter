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
        time.sleep(60)
        for post in db.fetch_all():
            if post[0] not in tuple(map(lambda x: x[-1], process_index)):
                post = Post(post[0], post[1], post[2], post[3], post[4], post[5])

                process = Process(target=manager, args=(post.bot_username, post))
                process.start()

                process_index.append((process, post.index))

        for process, index in process_index:
            if not process.is_alive():
                process_index.pop(process_index.index((process, index)))


if __name__ == '__main__':
    main()
