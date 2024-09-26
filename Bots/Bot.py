import random

from pytwitter import Api as TwitterAPI

from items import Post
from logger.logger import Logger

from typing import IO
from abc import ABC, abstractmethod


class Bot(ABC):
    def __init__(self, logger_name: str, bearer_token: str):
        self.api = TwitterAPI(bearer_token=bearer_token)
        self.logger: Logger = Logger(logger_name)

        self.logger.debug(f'{logger_name} initialized successfully')

    def __upload_media(self, media_type: str, media_file_path: str):
        """ post a tweet on X """
        file: IO = open(media_file_path, 'rb')

        response: dict = self.api.upload_media_chunked_init(
            media_type=media_type,
            total_bytes=file.seek(0, 2),
            return_json=True
        )

        print(response)  # TODO: Dont forget to test this, the response['media_id'] must be fixed
        self.api.upload_media_chunked_append(
            media_id=response['media_id'],
            segment_index=random.randint(0, 999),
            media=file
        )

        file.close()
        return self.api.upload_media_chunked_finalize(media_id=response['media_id'])

    def tweet_image(self, media_file_path: str):
        """ make an image post on X """
        if media_file_path.split('.')[-1] not in ['jpg', 'jpeg']: return False
        return self.__upload_media('image/jpeg', media_file_path)

    def tweet_video(self, media_file_path):
        """ make a video post on X """
        return self.__upload_media('video/mp4', media_file_path)

    def tweet_text(self, text_body: str):
        """ make a text post on X """
        return self.api.create_tweet(text=text_body)

    @abstractmethod
    def tweet(self, post: Post) -> bool:
        """ make a post on X """
