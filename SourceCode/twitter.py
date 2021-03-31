#!/usr/bin/env python3
"""Functions to use with Twitter/Tweepy"""
#
# Python Script:: twitter.py
#
# Linter:: pylint
#
# Copyright 2021, Matthew Ahrenstein, All Rights Reserved.
#
# Maintainers:
# - Matthew Ahrenstein: matt@ahrenstein.com
#
# See LICENSE
#

import json
import re
from datetime import date
import tweepy


def auth_to_twitter(credentials_file: str) -> tweepy.API:
    """
    Authenticate to Twitter using Tweepy and return a session

    Args:
        credentials_file: A credentials JSON file

    Returns:
            tweepy_session: A tweepy.API session
    """
    with open(credentials_file) as creds_file:
        data = json.load(creds_file)
    auth = tweepy.OAuthHandler(data['twitter']['consumer_key'], data['twitter']['consumer_secret'])
    auth.set_access_token(data['twitter']['access_key'], data['twitter']['access_secret'])
    api = tweepy.API(auth)
    return api


def get_user_tweet(user_id: int, tweepy_session: tweepy.API) -> str:
    """
    Get the tweet of a user and return it without invalid characters

    Args:
        user_id: The UID of the twitter user
        tweepy_session: A tweepy API session
    Returns:
        tweet_text: The text of the tweet in all lowercase
    """
    # Get the latest tweet using Tweepy
    latest_tweet = tweepy.Cursor(tweepy_session.user_timeline, id=user_id,
                                 since=date.today(), tweet_mode='extended').items(1)
    # Convert the latest tweet in to ASCII text only
    tweet_text = [re.sub('[^A-Za-z0-9]+', ' ', tweet.full_text) for tweet in latest_tweet]
    return tweet_text[0].lower()
