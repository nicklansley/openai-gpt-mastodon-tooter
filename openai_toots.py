import json
from datetime import time
from time import sleep

import mastodon
from mastodon import Mastodon
import openai
import requests
import threading

mastodon_api_base_url = ''
mastodon_client_id = ''
mastodon_client_secret = ''
mastodon_access_token = ''
accounts_whitelist = []


class Listener(mastodon.StreamListener):
    def on_update(self, status):
        print(f"on_update: {status}")

    def on_notification(self, notification):
        print(f"on_notification: {notification}")


# read environmant variables from a file
def read_env():
    global mastodon_api_base_url
    global mastodon_client_id
    global mastodon_client_secret
    global mastodon_access_token
    global accounts_whitelist

    with open('env.json') as f:
        env = json.load(f)
        openai.api_key = env['OPENAI_API_KEY']
        mastodon_api_base_url = env['MASTODON_API_BASE_URL']
        mastodon_client_id = env['MASTODON_CLIENT_ID']
        mastodon_client_secret = env['MASTODON_CLIENT_SECRET']
        mastodon_access_token = env['MASTODON_ACCESS_TOKEN']
        accounts_whitelist = env['MASTODON_REPLY_TO_ACCOUNTS_WHITELIST']



def connect_to_mastodon_account():
    global mastodon_api_base_url
    global mastodon_client_id
    global mastodon_client_secret
    global mastodon_access_token

    result = Mastodon(api_base_url=mastodon_api_base_url,
                      client_id=mastodon_client_id,
                      client_secret=mastodon_client_secret,
                      access_token=mastodon_access_token)
    return result


def call_openai(prompt):
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    return completion.choices[0].text.replace('\n', ' ').replace('\r', ' ').strip()


# Write a function that uses openai library to call Open AI's moderation to check id the text is safe
# If the text is safe return True, else return False
def is_message_content_flagged_as_unsafe(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    data = {
        "input": prompt
    }

    url = "https://api.openai.com/v1/moderations"

    r = requests.post(url, headers=headers, json=data)
    response = r.json()
    return response['results'][0]['flagged']


def strip_html_from_text(text):
    # find position in text od string '</span></a></span>'
    # remove everything before that
    start_position = text.find('</span></a></span>')
    filtered_text = text[start_position + 18:]
    # remove the final '</p>
    return filtered_text[:-4]


def get_unread_messages():
    unread_messages = []
    m = connect_to_mastodon_account()
    # Get the latest direct message
    conversations = m.conversations()
    for c in conversations:
        if c['unread']:
            try:
                new_message = {
                    'id': c['last_status']['id'],
                    'account': c['last_status']['account']['acct'],
                    'display_name': c['last_status']['account']['display_name'],
                    'content': strip_html_from_text(c['last_status']['content'])
                }
                unread_messages.append(new_message)
            except KeyError as ke:
                print('KeyError:', ke)
                print('Error processing message:', c)

        # mark the message as read
        m.conversations_read(c['id'])

    return unread_messages


def toot(toot_content, in_reply_to_id):
    mastodon = connect_to_mastodon_account()
    mastodon.status_post(status=toot_content, in_reply_to_id=in_reply_to_id, visibility='direct')
    print('Tooted', toot_content, 'in reply to', in_reply_to_id)


def run():
    global accounts_whitelist
    messages = get_unread_messages()
    if len(messages) > 0:
        for message in messages:
            if message['account'] in accounts_whitelist:
                if not is_message_content_flagged_as_unsafe(message['content']):
                    # If the message is safe, call open AI
                    openai_response = call_openai(message['content'])
                    toot('@{} - {}'.format(message['account'], openai_response), message['id'])
                else:
                    # If the message is not safe, toot a warning
                    toot('Sorry, @{}, your account is not whitelisted to access OpenAI.'.format(message['account']),
                         message['id'])
    else:
        print('No new messages to process')


def run_listening_thread():
    m = connect_to_mastodon_account()
    m.stream_user(Listener())


if __name__ == '__main__':
    # t = threading.Thread(target=run_listening_thread)
    # t.start()
    read_env()
    try:
        while True:
            run()
            # Sleep for 10 seconds
            sleep(10)
    except KeyboardInterrupt:
        print('Exiting...')
