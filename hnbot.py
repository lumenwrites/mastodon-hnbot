import os, sys

from mastodon import Mastodon
import feedparser


url = "http://hnrss.org/newest?points=100"
feed = feedparser.parse(url)
stories = feed["entries"]
# print(feed["entries"][0]["title"])
# print(list(stories[0].keys()))
# print(feed["updated"])
# print(feed["updated_parsed"])

def seen(myid):
    try:
        with open('seen.db', 'r') as f:
            if (str(myid) in [x.strip() for x in f.readlines()]):
                # If story is in the list of the seen stories - return 1
                return 1
            else:
                return 0
    except IOError as e:
        # catch non-existing SEENDB
        if e.errno == 2:
            return 0

def write_to_seen(myid):
    with open('seen.db', 'a') as f:
        f.write(str(myid))
        f.write('\n')        

# Make the list of stories who's id isn't in the seen list
unseen_stories = [story for story in stories if not seen(story["id"])]


try:
    instance_url = sys.argv[3]
except:
    instance_url = 'https://mastodon.social'

# Create app if doesn't exist
if not os.path.isfile("hnbot_clientcred.txt"):
    print("Creating app")
    mastodon = Mastodon.create_app(
        'HackerNewsBot',
        to_file = 'hnbot_clientcred.txt',
        api_base_url=instance_url
    )

# Fetch access token if I didn't already
if not os.path.isfile("hnbot_usercred.txt"):
    print("Logging in")
    mastodon = Mastodon(
        client_id = 'hnbot_clientcred.txt',
        api_base_url=instance_url        
    )
    email = sys.argv[1]
    password = sys.argv[2]
    mastodon.log_in(email, password, to_file = 'hnbot_usercred.txt')

# Login using generated auth
mastodon = Mastodon(
    client_id = 'hnbot_clientcred.txt',
    access_token = 'hnbot_usercred.txt',
    api_base_url=instance_url    
)


for story in unseen_stories:
    title = story["title"]
    storyid = story["id"]
    post = title + "\n" + storyid + "\n#hackernews #tech"
    write_to_seen(storyid)
    print("Posting " + post)
    mastodon.toot(post)
