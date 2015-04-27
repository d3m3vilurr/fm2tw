#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import tweepy
import sqlite3
import feedparser
import datetime
import time

STORE_VERSION = 1
DATE_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
DEFAULT_POST_FORMAT = "#NowPlaying \"{title}\" via Last.fm {link}"
CONFIG = yaml.load(file('config.yaml'))
DB_SESSION = None

def open_storage():
    global DB_SESSION
    if not DB_SESSION:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        curr_version, = cursor.fetchone()
        upgrade_storage(conn, curr_version, STORE_VERSION)
        cursor.execute("PRAGMA user_version = %d" % STORE_VERSION)
        DB_SESSION = conn
    return DB_SESSION

def upgrade_storage(db, old_version, new_version):
    curr_version = old_version
    if new_version == curr_version:
        return
    elif new_version < curr_version:
        downgrade_storage(db, old_version, new_version)
    else:
        cursor = db.cursor()
        if curr_version < 1:
            cursor.execute("""
                create table posts (
                    _id integer primary key,
                    message text not null,
                    updated text not null
                )
            """)
            cursor.execute("""
                create index posts_updated on posts(updated desc)
            """)
            curr_version += 1
        cursor.close()

def downgrade_storage(db, old_version, new_version):
    pass

def last_post():
    conn = open_storage()
    cursor = conn.cursor()
    cursor.execute("""
        select * from posts
         order by updated desc
         limit 1
    """)
    item = cursor.fetchone()
    if item:
        _id, msg, updated = item
        return dict(_id=_id, message=msg, updated=updated)
    else:
        return dict()

def get_lastfm(feed):
    items = feedparser.parse(feed).entries
    return items and items[0] or dict()

def _check_exist(scrob, last):
    title = scrob.get('title').encode('utf-8')
    updated = datetime.datetime \
                      .strptime(scrob.get('updated'), DATE_FORMAT)
    updated_range = (updated - datetime.timedelta(1./24)) \
                        .strftime("%Y-%m-%d %H:%M:%S")
    if (updated <= \
        datetime.datetime.utcnow() - datetime.timedelta(10./24/60)):
        print "SKIP OLD PLAY MUSIC: %s" % title
        return True
    if (last and last.get('message') == scrob.get('title') and \
        updated_range <= last.get('updated')):
        print "SKIP SAME MUSIC: %s" % title
        return True

def _save_storage(scrob):
    conn = open_storage()
    cursor = conn.cursor()
    query = """
        insert into posts(message, updated)
        values (?, ?)
    """
    updated = datetime.datetime \
                      .strptime(scrob.get('updated'), DATE_FORMAT)
    cursor.execute(
        query,
        (scrob.get('title'), updated.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()

def _post_twitter(scrob, post_format=None):
    post_format = post_format or DEFAULT_POST_FORMAT
    auth = tweepy.OAuthHandler(
        CONFIG["CONSUMER_KEY"],
        CONFIG["CONSUMER_SECRET"]
    )
    auth.set_access_token(
        CONFIG["ACCESS_TOKEN_KEY"],
        CONFIG["ACCESS_TOKEN_SECRET"]
    )
    api = tweepy.API(auth)
    dup = 0
    while True:
        title = scrob.get('title').encode('utf-8')
        title = len(title) < 100 and title or (title[:100] + '...')
        msg = post_format.format(
            title=title, link=scrob.get('link'),
            duplicate=dup and ("(%d)" % dup) or ""
        )
        try:
            api.update_status(status=msg)
            return
        except tweepy.TweepError:
            dup += 1

def new_post(scrob, last, post_format=None):
    title = scrob.get('title').encode('utf-8')
    print "NEW POST MUSIC: %s" % title
    _save_storage(scrob)
    _post_twitter(scrob, post_format)

def main():
    last = last_post()
    scrob = get_lastfm(CONFIG["LASTFM_FEED"])
    if _check_exist(scrob, last):
        return
    new_post(scrob, last, CONFIG.get("POST_FORMAT"))

if __name__ == "__main__":
    main()
