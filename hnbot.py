import argparse
import dbm
import os
import sys
from typing import Any, Iterable, Iterator, List, Optional

import feedparser
from mastodon import Mastodon


class Db:
    def __init__(self, points: int):
        self.handle = dbm.open("seen.db", "c")
        self.points = points

    def seen(self, id: str) -> bool:
        res = self.handle.get(self.hn_key(id), None)
        return res is not None

    def mark_seen(self, id: str):
        self.handle[self.hn_key(id)] = "seen"

    def hn_key(self, id) -> str:
        return f"hn{self.points}-{id}"

    def __getitem__(self, key: str) -> Optional[Any]:
        return self.handle.get(key, None)

    def __setitem__(self, key: str, value: Any):
        self.handle[key] = value


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("instance_url", help="Mastodon instance to post to")
    parser.add_argument("email", help="email used for login to Mastodon")
    parser.add_argument("password", help="password used for login to Mastodon")
    parser.add_argument(
        "--points",
        dest="points",
        default=50,
        type=int,
        help="Number of hackernews points before submitting",
    )
    parser.add_argument(
        "--bot-name", dest="bot_name", default="HackerNewsBot", help="Name of the bot"
    )
    return parser.parse_args()


def get_stories(db: Db, points: int) -> Iterator[feedparser.FeedParserDict]:
    feed = feedparser.parse(f"http://hnrss.org/newest?points={points}")
    stories = feed["entries"]
    return filter(lambda story: not db.seen(story["id"]), stories)


def create_client(
    db: Db,
    instance_url: str,
    email: str,
    password: str,
    bot_name: str = "HackerNewsBot",
) -> Mastodon:
    client_id = db["client_id"]
    client_secret = db["client_secret"]
    access_token = db["access_token"]
    if client_id is None or client_secret is None:
        client_id, client_secret = Mastodon.create_app(
            bot_name, api_base_url=instance_url
        )
        db["client_id"] = client_id
        db["client_secret"] = client_secret

    if access_token is None:
        mastodon = Mastodon(
            client_id=client_id, client_secret=client_secret, api_base_url=instance_url
        )
        access_token = mastodon.log_in(email, password)
        db["access_token"] = access_token

    return Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url=instance_url,
    )


def main() -> None:
    args = parse_arguments()
    db = Db(args.points)
    stories = get_stories(db, args.points)

    mastodon = create_client(
        db, args.instance_url, args.email, args.password, args.bot_name
    )

    for story in stories:
        title = story["title"]
        storyid = story["id"]
        links = story["links"]
        if len(links) > 0:
            link = f"{links[0]['href']} ({storyid})"
        else:
            link = f"{storyid}"

        post = f"{title} {link}"
        print("Posting " + post)
        db.mark_seen(storyid)
        mastodon.toot(post)


if __name__ == "__main__":
    main()
