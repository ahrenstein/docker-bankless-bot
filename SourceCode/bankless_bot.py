#!/usr/bin/env python3
"""A bot that buys and sells ETH based on tweets from certain Bankless folks."""
#
# Python Script:: bankless_bot.py
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

from itertools import count
import argparse
import datetime
import time
import twitter
import coinbase_pro


def main(credentials_file: str, currency: str, price: float, trigger_phrase: str):
    """
    The main function that triggers and runs the bot functions

    Args:
    credentials_file: Path to the JSON file containing credentials
    currency: The crypto currency that you want to trade
    price: The USD buy price you are willing to pay
    trigger_phrase: The trigger phrase in the tweets
    """
    # Twitter account IDs courtesy of https://tweeterid.com/
    twitter_accounts = {"Bankless": 1225557966142820354,
                        "Ryan Sean Adams": 14571055,
                        "David Hoffman": 981208355115974656}
    # Execute the bot every 10 seconds
    for cycle in count():
        now = datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S")
        print("LOG: Cycle %s: %s" % (cycle, now))
        print("LOG: Transacting on %s @ %s when \"%s\" is heard"
              % (currency, price, trigger_phrase))
        # Get Twitter API credentials
        twitter_api = twitter.auth_to_twitter(credentials_file)
        for account, user_id in twitter_accounts.items():
            tweet = twitter.get_user_tweet(user_id, twitter_api).lower()
            if trigger_phrase.lower() in tweet:
                print("LOG: Trigger phrase found"
                      " in %s's latest tweet. Continuing cycle..." % account)
                coinbase_pro.engage_trade(credentials_file, currency, price)
            # else:
                # print("LOG: Trigger phrase NOT found in"
                #      " %s's latest tweet. Ending cycle...." % account)
        time.sleep(10)


if __name__ == '__main__':
    # This function parses and return arguments passed in
    # Assign description to the help doc
    PARSER = argparse.ArgumentParser(
        description='A bot that buys and sells ETH'
                    ' based on tweets from certain Bankless folks.')
    # Add arguments
    PARSER.add_argument(
        '-c', '--credsFile', type=str, help="Path to credentials.json file", required=True
    )
    PARSER.add_argument(
        '-t', '--triggerPhrase', type=str, help="The trigger phrase to transact on",
        default="Ultra Sound Money", required=False
    )
    PARSER.add_argument(
        '--currency', type=str, help="Choose the crypto currency", default='ETH', required=False
    )
    PARSER.add_argument(
        '--price', type=float, help="Choose the USD buy price", default=50.00, required=False
    )
    # Array for all arguments passed to script
    ARGS = PARSER.parse_args()
    ARG_CREDS = ARGS.credsFile
    ARG_CURRENCY = ARGS.currency
    ARG_PRICE = ARGS.price
    ARG_TRIGGER_PHRASE = ARGS.triggerPhrase
    main(ARG_CREDS, ARG_CURRENCY, ARG_PRICE, ARG_TRIGGER_PHRASE)
