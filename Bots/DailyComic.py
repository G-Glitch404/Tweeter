import os

from typing import Optional

from Bots import Bot
from items import Post
from util.utils import get_filename
from Crawlers.RedditCrawler import RedditAPI


class DailyComic(Bot):
    def __init__(self, proxy: Optional[str] = None) -> None:
        super(DailyComic, self).__init__(logger_name='DailyComic', bearer_token=os.environ['DAILY_COMIC_BEARER_TOKEN'])

        if hasattr(self, 'tweet_image'): self.tweet_image = None
        if hasattr(self, 'tweet_video'): self.tweet_video = None
        if hasattr(self, 'tweet_text'): self.tweet_text = None

        self.reddit_api: RedditAPI = RedditAPI(proxy=proxy)

    def post_image(self, post: Post):
        """ post an image """
        self.logger.debug(f'posting an image to Twitter filename: "{get_filename(post.media_file_path)}"')
        return super().tweet_image(media_file_path=post.media_file_path)

    def post_video(self, post: Post):
        """ post a video """
        self.logger.debug(f'posting a video to Twitter filename: "{get_filename(post.media_file_path)}"')
        return super().tweet_video(media_file_path=post.media_file_path)

    def post_text(self, post: Post):
        """ post a text """
        self.logger.debug(f'posting a text to Twitter body: "{post.body}"')
        return super().tweet_text(text_body=post.body)

    def tweet(self, post: Post):
        """ make a post on X """
        if post.post_type == 'image': return self.post_image(post)
        if post.post_type == 'video': return self.post_video(post)
        if post.post_type == 'text': return self.post_text(post)

        self.logger.error(f'post type "{post.post_type}" not supported')
        return False
