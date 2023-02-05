# GPT-TOOTER
## A GPT-3 based Mastodon bot

If you fancy asking AI's opinion by tooting directly to it, you can use this bot. It's a simple Python script that uses the [OpenAI API](https://openai.com/blog/openai-api/) to generate a response to your toots. It's a bit like a Twitter bot, but for Mastodon.

### How to use it
Fill in the details in env.json with your Open AI key and the access credentials of your bot's Mastodon account.
The OpenAI key will be avalable in your account at OpenAI. Once you are logged in, head to:
https://platform.openai.com/account/api-keys

You can find the Mastodon details by logging in to your account on your mastoson instance's web site, and selecting:
- Preferences
- Development
- Clicking 'New Application'
- Filling in the application name and ensuring 'read', and 'write' are selected
- Click 'Submit'
- You'll go back to your list of application(s) - select the one you just created

You'll then get keys that look like this (which I have now rendered useless on my account!):
<pre>
Client key:	0Gj2v3chBz1LaWVo5JeEkO17NXGBEfaeRD2Wzi0YxX4
Client secret:	ZZ1ffuvu8FHk2LGTikGbrVGCWWysSFqCNt3S0zHGHno
Your access token:	dGTeJHxir7JfwHPxjq5LRy6AQbOeWueCazUkPUQ491c
</pre>

Make sure you are using Python 3.9 (at this date, openai has issues with python 3.10 not able to find aiohttp)

Set up pip to install the requirements:
<pre>
pip install -r requirements.txt
</pre>

... and set it running!
<pre>
python openai_toots.py
</pre>

If running on a server, add this to your crontab to run it at bootup.
You don't need to be root to do this, just run:
<pre>crontab -e</pre>
... and add this line:
<pre>
@reboot python /path/to/gpt-tooter.py
</pre>
