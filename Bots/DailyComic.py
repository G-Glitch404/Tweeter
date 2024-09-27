from datetime import datetime as dt
from Bots.Bot import Bot
from items import Post
from typing import Union
from util.utils import path, get_filename


class DailyComic(Bot):
    def __init__(self) -> None:
        super(DailyComic, self).__init__(logger_name='DailyComic')
        if hasattr(self, 'tweet_image'): self.tweet_image = None
        if hasattr(self, 'tweet_video'): self.tweet_video = None
        if hasattr(self, 'tweet'): self.tweet = None
        if hasattr(self, 'tweet_text'): self.tweet_text = None

    def post_image(self, post: Post) -> Union[dict, bool]:
        """ post an image """
        self.logger.debug(f'posting an image to Twitter filename: "{get_filename(post.media_file_path)}"')
        media_id: str = super().tweet_image(self.api, media_file_path=post.media_file_path)
        return super().tweet(self.api, media_id, post)

    def post_video(self, post: Post) -> Union[dict, bool]:
        """ post a video """
        self.logger.debug(f'posting a video to Twitter filename: "{get_filename(post.media_file_path)}"')
        media_id: str = super().tweet_video(self.api, media_file_path=post.media_file_path)
        return super().tweet(self.api, media_id, post)

    def post_text(self, post: Post):
        """ post a text """
        self.logger.debug(f'posting a text to Twitter body: "{post.body}"')
        return super().tweet_text(self.api, text_body=post.body)

    def post(self, post: Post) -> Union[dict, bool]:
        """ make a post on X """
        if post.post_type == 'image': return self.post_image(post)
        if post.post_type == 'video': return self.post_video(post)
        if post.post_type == 'text': return self.post_text(post)

        self.logger.error(f'post type "{post.post_type}" not supported')
        return False


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()
    post_ = Post(
        index=0,
        post_type='image',
        body='body',
        media_file_path=path('media', 'test.jpg'),
        upload_date=dt.today(),
        bot_username='NewDayNewComic'
    )
    bot = DailyComic()
    bot.tweet(post_)
