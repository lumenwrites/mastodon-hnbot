A bot posting the Hacker News stories with 100+ points to [Mastodon](https://github.com/tootsuite/mastodon).

https://hackertribe.io/@HackerNewsBot

![](https://raw.githubusercontent.com/raymestalez/mastodon-hnbot/master/screenshot.png)

# Usage

Create an account for the bot. For convenience you can use youremail+hnbot@gmail.com, to avoid registering separate email.

Then run the command:

```python3 ./hnbot.py "youremail@gmail.com" "yourpassword" "https://insancename.com"```

# Run it regularly

You can use cron to run the bot regularly.

Run the command:

```crontab -e```

And at the end of the file add the lines:

```0,30 * * * * python3 /path/to/the/script/hnbot.py "youremail@gmail.com" "yourpassword" "https://insancename.com"```
