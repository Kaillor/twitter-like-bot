import configparser
import os
import sys
import rauth
import requests


def twitter_like_bot():
    os.system('color')

    config = configparser.RawConfigParser()
    config.read('settings.cfg')

    # get parameters
    try:
        twitter_api_key = config['KEYS']['twitter_api_key']
        twitter_api_secret = config['KEYS']['twitter_api_secret']
        bearer_token = config['KEYS']['bearer_token']
        username = config['PARAMS']['username']
        since_id = config['PARAMS']['since_id']
    except KeyError:
        print(
            "\n\033[91mFailed to load settings!\033[0m"
            "\nCreate a file named 'settings.cfg' with the following content:"
            "\n\n[KEYS]"
            "\ntwitter_api_key = <key>"
            "\ntwitter_api_secret = <secret>"
            "\nbearer_token = <token>"
            "\n\n[PARAMS]"
            "\nusername = <account of which to like tweets>"
            "\nsince_id = 0"
        )
        sys.exit()

    # create session
    try:
        twitter = rauth.OAuth1Service(
            name='twitter',
            consumer_key=twitter_api_key,
            consumer_secret=twitter_api_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            base_url='https://api.twitter.com/1.1/')
        request_token, request_token_secret = twitter.get_request_token(
            params={'oauth_callback': 'oob'}
        )
        authorize_url = twitter.get_authorize_url(request_token)

        print(
            "\nVisit this URL to authorize the app or type 'q' to quit."
            f"\n\033[94m{authorize_url}\033[0m"
        )
        pin = input("PIN: ")
        if pin == "q":
            sys.exit()

        session = twitter.get_auth_session(
            request_token,
            request_token_secret,
            method='POST',
            data={'oauth_verifier': pin})
    except requests.exceptions.ConnectionError:
        print("\n\033[91mConnection failed!\033[0m")
        sys.exit()
    except KeyError:
        print("\n\033[91mAuthorization failed!\033[0m")
        sys.exit()

    try:
        # get user id
        user_request = requests.get(
            f"https://api.twitter.com/2/users/by/username/{username}",
            headers={"authorization": f"bearer {bearer_token}"})
        user_dict = user_request.json()
        user_request.close()
        user_id = user_dict['data']['id']

        # get ids of new tweets
        tweets_request = session.get(
            f"https://api.twitter.com/2/users/{user_id}/tweets",
            header_auth=True,
            params={'since_id': since_id, 'max_results': '100'})
        tweets_dict = tweets_request.json()
        tweets_request.close()
        newest_tweet_id = tweets_dict['meta']['newest_id']

        tweet_ids = []
        for tweet in tweets_dict['data']:
            tweet_ids.append(tweet['id'])

        while 'next_token' in tweets_dict['meta'] and len(tweet_ids) < 200:
            tweets_request = session.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                header_auth=True,
                params={
                    'since_id': since_id,
                    'max_results': '100',
                    'pagination_token': tweets_dict['meta']['next_token']
                }
            )
            tweets_dict = tweets_request.json()
            tweets_request.close()
            for tweet in tweets_dict['data']:
                tweet_ids.append(tweet['id'])

        # like tweets
        liked_tweets = 0
        limit_reached = False
        for tweet_id in tweet_ids:
            like_request = session.post(
                "https://api.twitter.com/1.1/favorites/create.json",
                header_auth=True,
                data={'id': tweet_id})
            if like_request.status_code == 200:
                liked_tweets += 1
            elif like_request.status_code == 429:
                print("\n\033[91mLimit reached!\033[0m")
                limit_reached = True
                break

    except requests.exceptions.ConnectionError:
        print("\n\033[91mConnection interrupted!\033[0m")
        sys.exit()
    except KeyError:
        print("\nNo Tweets found.")
        sys.exit()

    # set since_id
    print(f"\n\033[92mLiked {liked_tweets} Tweets, Retweets and Replies!\033[0m")
    if not limit_reached:
        config.set('PARAMS', 'since_id', newest_tweet_id)
        with open('settings.cfg', 'w') as configfile:
            config.write(configfile)


if __name__ == '__main__':
    twitter_like_bot()
