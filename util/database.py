import sqlite3
import threading

from settings import settings
from util.decorators import catch_exceptions
from util.utils import path


class Database(threading.Thread):
    posts_table_file = path('.db', path('sql', 'posts.sql'))
    tweets_table_file = path('.db', path('sql', 'tweets.sql'))

    def __init__(self, database_filename: str = settings["POSTS_DATABASE"]) -> None:
        super(Database, self).__init__()
        self.conn = sqlite3.connect(database_filename, check_same_thread=False, timeout=120.0)
        self.cursor = self.conn.cursor()

        self.create_tables()

    def create_tables(self) -> None:
        """ Create tables in database """
        self.cursor.execute(open(self.posts_table_file).read())
        self.cursor.execute(open(self.tweets_table_file).read())
        self.conn.commit()

    def fetch_all(self, table_name: str = 'posts') -> tuple:
        """
        Fetch all data from table

        :yield: (id, profile) in a tuple
        """
        for article in self.cursor.execute(f'SELECT * FROM {table_name};').fetchall():
            yield article

    @catch_exceptions
    def insert_post(self, record: tuple) -> bool:
        """
        insert a record to the tweets table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute('INSERT INTO posts ([post_type], [text_body], [media_file_path], [upload_date], [bot_username]], [hash]) VALUES (?, ?, ?, ?, ?, ?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    @catch_exceptions
    def insert_tweet(self, record: tuple) -> bool:
        """
        insert a posted tweet to the tweets table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute('INSERT INTO tweets ([post_type], [text_body], [media_file_path], [upload_date], [bot_username], [hash]) VALUES (?, ?, ?, ?, ?, ?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    def delete_record(self, record_id: int, table_name: str = 'posts') -> None:
        """ Delete a record from a table """
        self.cursor.execute(f'DELETE FROM {table_name} WHERE id={record_id};')
        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def __del__(self) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
