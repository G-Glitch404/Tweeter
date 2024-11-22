from multiprocessing import Process
from datetime import datetime, timedelta
from typing import Union

from util.database import Database
from util.decorators import catch_exceptions
from items import Post
from Manager import manager
from settings import settings
from logger.logger import Logger
from Crawlers.RedditCrawler import RedditAPI
from dotenv import load_dotenv

load_dotenv()


@catch_exceptions
def recon(subreddits: Union[list[str], str], bot_username) -> Process:
    last_post_datetime: datetime = datetime.now()  # only declared once
    logger: Logger = Logger('RedditRecon')
    db: Database = Database(settings['POSTS_DATABASE'])
    reddit: RedditAPI = RedditAPI()

    if isinstance(subreddits, str):
        subreddits: list[str] = [subreddits]

    for subreddit in subreddits:
        logger.info(f'scanning subreddit: {subreddit} for any new posts')
        for post in reddit.get_community_posts(subreddit, posts_count=5):
            if not post or (post["upvotes"] < 100 or post["postNsfw"]): continue

            last_post_datetime += timedelta(minutes=30)
            post["postType"] = post["postType"].lower().replace(' ', '')
            if post["postType"] == "video" and post["postVideoLink"]:
                media_path: str = reddit.download_media(post["postVideoLink"])
                db_post: list = [post["postIndex"], "video", post["title"] or post["body"], media_path, None, bot_username]

            elif post["postType"] == "image" and post["postImageLink"]:
                media_path: str = reddit.download_media(post["postImageLink"])
                db_post: list = [post["postIndex"], "image", post["title"] or post["body"], media_path, None, bot_username]

            elif post["postType"] == "link":
                title = f"{post['title']}\n{post["postContentLink"]}"
                db_post: list = [post["postIndex"], "text", title, None, None, bot_username]

            elif post["postType"] == "text":
                db_post: list = [post["postIndex"], "text", post["body"] or post["title"], None, None, bot_username]

            else:
                logger.error(f'got a reddit post with unsupported media type: "{post["postType"]}"'); continue

            if len(db_post[1]) > 280: continue  # twitter limits to 280 characters

            db_post += [bin(hash(tuple(db_post))), ]
            db_post[4] = last_post_datetime  # adding the upload_time here, so it doesn't change the value hash from db hash
            if not db.insert_tweet(db_post[1:]):
                logger.warning(f'post with link "{post['postLink']}" is a duplicate, skipping it.'); continue

            db_post: Post = Post(*db_post)
            logger.info(f'found a new post in subreddit "{subreddit}" link: "{post['postLink']}" scheduling it for upload')

            process: Process = Process(target=manager, args=(db_post.bot_username, db_post))
            process.start()

            return process
    return Process()


if __name__ == '__main__':
    import time

    while True:
        for subreddit_ in settings['RECON_SUBREDDITS']:
            recon(subreddit_, 'NewDayNewComic')
        time.sleep(60*60)
