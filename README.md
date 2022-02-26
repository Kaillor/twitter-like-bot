# Twitter Like Bot
This script will automatically like the last 200 Tweets, Retweets and Replies of a given account. To use it, a Twitter Developer Account is necessary to create an App with OAuth 1.0a turned on. Information about Twitter Developer Apps can be found [here](https://developer.twitter.com/en/docs/apps/overview).
Create a file named 'settings.cfg' in the projects root directory with the following content:
```
[KEYS]
twitter_api_key = <key>
twitter_api_secret = <secret>
bearer_token = <token>

[PARAMS]
username = <account of which to like tweets>
since_id = 0
```