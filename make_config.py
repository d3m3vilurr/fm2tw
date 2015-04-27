#!/usr/bin/env python
import tweepy

def main(filename='config.yaml'):
    #print "First create your application: https://dev.twitter.com/apps"
    #CONSUMER_KEY = raw_input("Consumer key? ").strip()
    #CONSUMER_SECRET = raw_input("Consumer secret? ").strip()
    CONSUMER_KEY = "7eRve9CnBu9zngpU9ILBg"
    CONSUMER_SECRET = "ar7ow7RL6kkJnaFaJm3dKVHzTghBidzRarR9GNASOc"

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth_url = auth.get_authorization_url()
    print "Auth check: " + auth_url
    pin = raw_input("PIN code? ").strip()
    auth.get_access_token(pin)
    ACCESS_TOKEN_KEY = auth.access_token
    ACCESS_TOKEN_SECRET = auth.access_token_secret
    lastfm = raw_input("LASTFM ID? ").strip()
    LASTFM_FEED = \
        "http://ws.audioscrobbler.com/2.0/user/%s/recenttracks.rss" % lastfm
    f = open(filename, "w")
    f.write("CONSUMER_KEY: %s\n" % CONSUMER_KEY)
    f.write("CONSUMER_SECRET: %s\n" % CONSUMER_SECRET)
    f.write("ACCESS_TOKEN_KEY: %s\n" % ACCESS_TOKEN_KEY)
    f.write("ACCESS_TOKEN_SECRET: %s\n" % ACCESS_TOKEN_SECRET)
    f.write("LASTFM_FEED: %s\n" % LASTFM_FEED)

if __name__ == "__main__":
    main()
