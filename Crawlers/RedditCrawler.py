import json

from typing import Union, Optional
from parsel import Selector

from util.decorators import catch_exceptions
from util.utils import clean_text, path
from util.session import Session
from util.selector import select as se
from logger.logger import Logger


class RedditAPI(Session):
    def __init__(self, proxy: str = None) -> None:
        super(RedditAPI, self).__init__()

        self.logger = Logger('RedditScraper')
        if proxy: self.proxies = {"http": proxy, "https": proxy}

    def __get_posts(self, posts_count: int, selector: Selector) -> list[dict]:
        """ extract the post data from the selector """
        def scrape(select: Selector) -> list[dict]:
            return [
                {
                    "postId": post.css(se['post_id']).get('') or None,
                    "authorId": post.css(se['author_id']).get('') or None,
                    "subredditId": post.css(se['subreddit_id']).get('') or None,
                    "subreddit": post.css(se['subreddit']).get(),
                    "author": author,
                    "title": post.css(se['post_title']).get(),
                    "postNsfw": not bool(post.css(se['post_nsfw']).get('0')),
                    "postType": post.css(se['post_type']).get(),
                    "postFlairs": clean_text(' '.join(post.css(se['post_flairs']).extract() or [])) or None,
                    "postIndex": int(post.css(se['post_index']).get('0')),
                    "commentsCount": int(post.css(se['comments_count']).get('0')),
                    "upvotes": int(post.css(se['post_upvotes']).get('0')),
                    "body": clean_text(''.join(post.css(se['content']).extract() or [])) or None,
                    "timestamp": post.css(se['timestamp']).get('').split('.')[0] or None,
                    "postLink": se['api_address'] + link if (link := post.css(se['post_link']).get()) else None,
                    "postContentLink": post.css(se['post_content_link']).get() if post.css(se['post_type']).get() == "link" else None,
                    "postImageLink": link if (link := post.css(se['post_content_link']).get()) and link.split('.')[-1] in ['jpeg', 'jpg'] else None,
                    "postVideoLink": link + '/HLS_480.ts' if (link := post.css(se['post_content_link']).get()) and len(link) <= 20 else None,
                    "authorAvatarLink": post.css(se['icon']).get(),
                }
                for post in select.css(se['post'])
                if (author := post.css(se['post_author']).get('')) and ('automoderator' not in author.lower() or 'bot' not in author.lower())
            ]

        posts: list = []

        if posts_count is None: posts_count: int = 10

        page = scrape(selector)
        if len(page) <= 0:
            self.logger.warning(f'no posts found for the selected subreddit or subreddit was not found')
            return page

        self.logger.info(f'scraping {posts_count} posts from subreddit {page[0]["subreddit"]}')
        posts.extend(page)
        for post in page: yield post

        next_link = lambda: selector.css(se['posts_cursor']).get()
        last_pull_count: int = 0
        while next_link() and len(posts) < posts_count:
            response: str = self.get(se['api_address'] + next_link()).text
            selector: Selector = Selector(text=response, type="html")
            page = scrape(selector)
            posts.extend(page)

            if last_pull_count == len(posts): break
            last_pull_count = len(posts)

            for post in page: yield post

        self.logger.info(f'scraped and found {len(posts)} posts from subreddit {page[0]["subreddit"]}')

    def get_user_info(self, user_name: str) -> dict:
        """ scraping a user information """
        if '/' in user_name: user_name = user_name.replace('/', ' ').strip().split(' ')[-1]
        self.logger.debug(f'scraping all info from user: {user_name}')

        response = self.get(se['api_address'] + f'/user/{user_name.replace(" ", "")}/').text
        selector = Selector(text=response, type="html")
        profile = json.loads(selector.css(se['user_profile']).get(
            json.dumps({'profile': {"empty": True}})  # if user-profile is empty then default to this dict
        ))['profile']

        return {
            "id": profile.get('id', None),
            "name": profile.get('name', None),
            "nsfw": profile.get('isNsfw', None),
            "description": clean_text(' '.join(selector.css(se['user_description']).extract())) or None,
            "post_karma": int(clean_text(selector.css(se["posts_karma"]).get('0')).replace(',', '')),
            "comment_karma": int(clean_text(selector.css(se['comments_karma'])[-1].css('::text').get('0')).replace(',', '')),
            "cake_day": clean_text(' '.join(selector.css(se['cake_day']).extract())).lower() or None,
            "icon": profile.get('icon', None),
        }

    def get_community_info(self, community_name: str) -> dict:
        """ scraping a subreddit information """
        if '/' in community_name: community_name = community_name.replace('/', ' ').strip().split(' ')[-1]
        self.logger.info(f'scraping all info from community: {community_name}')

        response = self.get(se['api_address'] + f'/r/{community_name.replace(" ", "")}/').text
        selector = Selector(text=response, type="html")
        subreddit = json.loads(selector.css(se['subreddit_homepage']).get(
            json.dumps({'subreddit': {"empty": True}})
        ))['subreddit']

        return {
            "id": subreddit.get('id', None),
            "name": subreddit.get('name', None),
            "title": selector.css(se['subreddit_title'].replace("{community_name}", community_name)).extract_first(None),
            "prefix": subreddit.get('prefixedName', None),
            "nsfw": subreddit.get('isNsfw', None),
            "quarantined": subreddit.get('isQuarantined', None),
            "description": selector.css(se['subreddit_description'].replace("{community_name}", community_name)).get('') or None,
            "subscribers": int(selector.css(se['subreddit_members_count'].replace("{community_name}", community_name)).get('0')),
            "online": int(selector.css(se['subreddit_online_members_count']).get('0')),
            "mods": [
                mod.replace('/', ' ').strip().split(' ')[-1]
                for mod in selector.css(se['subreddit_moderators']).extract() or ['']
                if mod
            ] or None,
            "rules": clean_text(' '.join(selector.css(se['subreddit_rules']).extract())).split('.') or None,
            'icon': subreddit.get('communityIcon', None)
        }

    def get_user_posts(self, user_name: str, posts_count: int = 100) -> list[dict]:
        """  scraping an amount of posts from a user """
        if '/' in user_name: user_name = user_name.split('/')[-1]
        self.logger.info(f'scraping {posts_count} from user: u/{user_name}')

        response: str = self.get(se['api_address'] + f'/user/{user_name}/submitted').text
        selector: Selector = Selector(text=response, type="html")

        return self.__get_posts(posts_count, selector)

    def get_community_posts(self, community_name: str, posts_count: int = 100) -> list[dict]:
        """ scraping an amount of posts from a subreddit """
        if '/' in community_name: community_name = community_name.split('/')[-1]
        self.logger.debug(f'scraping {posts_count} from subreddit: r/{community_name}')

        response: str = self.get(se['api_address'] + f'/r/{community_name}').text
        selector: Selector = Selector(text=response, type="html")

        return self.__get_posts(posts_count, selector)

    def get_home_feed_posts(self, posts_count: int = 100) -> list[dict]:
        """ scraping an amount of posts from the homa page feed for browsing reddit normally """
        self.logger.info(f'scraping {posts_count} from account home feed')

        response: str = self.get(se['api_address'] + '/?feed=home').text
        selector: Selector = Selector(text=response, type="html")

        yield from self.__get_posts(posts_count, selector)

    @catch_exceptions
    def download_media(self, media_link: str, filename: Optional[str] = None) -> Union[str, bool]:
        if "http" not in media_link:
            self.logger.error(f'url "{media_link}" is an invalid url')
            return False

        self.logger.info(f'downloading media from url: "{media_link}" please standby this might take a few minutes...')

        url_filename: str = media_link.split('?')[0].replace("/", " ").strip().split()[-1]
        with open(f"{filename or path("media", url_filename)}", 'wb') as file:
            content: bytes = self.get(media_link, headers={
                "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.5"
            }).content
            file.write(content)

        return file.name


if __name__ == '__main__':
    import random

    crawler = RedditAPI()
    videos = [item for item in crawler.get_community_posts('Unexpected', 10)]
    video = random.choice(videos)
    filename_ = crawler.download_media(video['postVideoLink'], path('media', 'test_video.mp4'))
    print(filename_)
