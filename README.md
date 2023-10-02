Deprecated
==========
This bot was fun to run but for now I'm archiving this repo. This bot was not used heavily and the changes to Twitter's API have resulted in this not being worth maintaining for now.

Bankless ETH Buying Bot
=======================
This bot is designed to buy ETH on Coinbase Pro every time one of the following Twitter accounts calls ETH "Ultra Sound Money"
(Note: I will update the documentation and docker container whenever the meme changes)

1. [Bankless](https://twitter.com/BanklessHQ)
2. [Ryan Sean Adams](https://twitter.com/RyanSAdams)
3. [David Hoffman](https://twitter.com/TrustlessState)

Bot rules:

1. The bot will place a market order for $50USD of $ETH every time one of the above Twitter accounts references the case-insensitive phrase "ultra sound money".
2. The bot will take profit at 10% via sell limit order
3. No orders will be placed if an existing buy/sell order is open on $ETH
4. The bot will not transfer money in to Coinbase so if there is not enough money available the bot will not trade.

Inspiration
-----------
The initial inspiration for this bot came from the Bankless community's massive faith in Ethereum and my desire to practice some Python 

Running The Bot
---------------
To run the bot you will need Docker and docker-compose installed on your computer.  

    docker-compose up -d

Config File
-----------
You will need the following credentials:

1. Twitter developer account credentials (Used by the Tweepy API)
2. Coinbase Pro credentials tied to the portfolio you want to run the bot against

These credentials should be in a configuration file named `credentials.json` and placed in `./config`.
Additionally, you can override the volume mount to a new path if you prefer.
The file should look like this:

```json
{
  "twitter": {
    "consumer_key": "YOUR_CONSUMER_KEY",
    "consumer_secret": "YOUR_CONSUMER_SECRET",
    "access_key": "YOUR_ACCESS_KEY",
    "access_secret": "YOUR_ACCESS_SECRET"
  },
  "coinbase": {
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "passphrase": "YOUR_API_PASSPHRASE"
  }
}
```

Override Parameters
-------------------

You can override a few parameters by changing the Docker CMD. The included [docker-compose.yml](docker-compose.yml) file
has an example that overrides the trigger phrase, price, and crypto currency used.

An example of doing this outside of Docker:

```bash
python SourceCode/bankless-bot.py -c /path/to/credentionals.json -t "Tesla now accepts bitcoin", --price 150.00 --currency BTC
```

Logs
----
The bot will log activity to stdout, so you can review it with `docker logs`

Donations
---------
I have configured GitHub Sponsors, if you would like to support my work.

Special Thanks
--------------
A special thanks to [Bankless](https://banklesshq.com/) for the informative newsletter and wonderfully helpful community.
