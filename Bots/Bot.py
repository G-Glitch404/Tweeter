import time

from typing import Union

from pytwitter import Api as TwitterAPI
from pytwitter.error import PyTwitterError
from pytwitter.models import MediaUploadResponse

from items import Post
from util.decorators import catch_exceptions
from logger.logger import Logger


class Bot:
    def __init__(
            self,
            logger_name: str,
            consumer_key: str,
            consumer_secret: str,
            access_token: str,
            access_secret: str) -> None:
        """ base bot class and functionality inherit this to create a new bot """
        self.api = TwitterAPI(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_secret=access_secret,
        )

        self.logger: Logger = Logger(logger_name)
        self.logger.debug(f'{logger_name} initialized successfully')

    @catch_exceptions
    def __upload_media(self, media_type: str, media_file_path: str) -> Union[bool, str]:
        """ post a tweet on X """
        file = open(media_file_path, 'rb')
        file_size: int = file.seek(0, 2); file.seek(0)

        response: dict = self.api.upload_media_chunked_init(
            media_type=media_type,
            media_category='tweet_video' if media_type == 'video/mp4' else None,
            total_bytes=file_size,
            return_json=True
        )

        if not response["media_id"]:
            self.logger.error(f'failed to upload media with media_type: "{media_type}" and media_file_path: "{media_file_path}"')
            return False

        self.api.upload_media_chunked_append(
            media_id=response['media_id'],
            segment_index=0,
            media=file
        )

        self.api.upload_media_chunked_finalize(media_id=response['media_id_string'])
        file.close()

        starting_wait_time: float = time.time()
        while time.time() - starting_wait_time <= 120:  # adding a safety 2 minutes timeout.
            try: upload_status: MediaUploadResponse = self.api.upload_media_chunked_status(media_id=response['media_id_string'])
            except PyTwitterError:
                self.logger.warning('error while uploading media - media might be uploaded, check before trying again')
                return response['media_id_string']
            else: time.sleep(upload_status.processing_info.check_after_secs or 5)

            if upload_status.processing_info.state == 'succeeded':
                self.logger.info(f'successfully uploaded media with media_id: {response["media_id_string"]}')
                return response['media_id_string']

            if upload_status.processing_info.state == 'failed':
                self.logger.error(f'failed to upload media_file_path: "{media_file_path}" reason: {upload_status.processing_info.error}')
                return False

        self.logger.error(f'failed to upload media with media_type: "{media_type}" and media_file_path: "{media_file_path}" reason timeout reached.')
        return False

    def tweet_text(self, text_body: str):
        """ make a text post on X """
        return self.api.create_tweet(text=text_body)

    def tweet_image(self, media_file_path: str):
        """ make an image post on X """
        if media_file_path.split('.')[-1] not in ['jpg', 'jpeg']:
            self.logger.error(f'file type ".{media_file_path.split(".")[-1]}" is not supported only supported types are (".jpg", ".jpeg")')
            return False
        return self.__upload_media('image/jpeg', media_file_path)

    def tweet_video(self, media_file_path):
        """ make a video post on X """
        if not media_file_path.split('.')[-1] == 'mp4':
            self.logger.error(f'file type ".{media_file_path.split(".")[-1]}" is not supported only supported types are (".mp4", )')
            return False

        return self.__upload_media('video/mp4', media_file_path)

    def tweet(self, media_id: str, post: Post) -> Union[dict, bool]:
        """ post media on X """
        if not media_id: self.logger.error(f'invalid media_id provided value: "{media_id}"'); return False
        self.logger.info(f'tweeting with media_id: "{media_id}" on page username: "{post["bot_username"]}"')
        return self.api.create_tweet(
            text=post['body'],
            media_media_ids=[str(media_id)],
            return_json=True
        )

    @catch_exceptions
    def post(self, post: Post):
        """ make a text post on X """
        if post.post_type == 'text':
            self.tweet_text(post.body)
            return True

        elif post.post_type == 'image':
            media_id: str = self.tweet_image(post.media_file_path)
            self.tweet(media_id, post)
            return True

        elif post.post_type == 'video':
            media_id: str = self.tweet_video(post.media_file_path)
            self.tweet(media_id, post)
            return True

        else:
            self.logger.error(f'post type "{post.post_type}" not supported')
            return False
