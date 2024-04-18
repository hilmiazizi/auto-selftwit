import requests
import os
import re
import random
from bs4 import BeautifulSoup
import asyncio
import twitter
from datetime import datetime, timedelta
import time
os.system('clear')

def compute_sleep_time(source_len, current_time=datetime.now()):

    total_sleep_time = 24 * 60 * 60

    source_len = max(source_len, 1)


    sleep_per_action = total_sleep_time / source_len

    remaining_time = (current_time + timedelta(days=1)) - current_time

    return remaining_time.total_seconds() / source_len

def remove_tags(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.findAll('a'):
        text = tag.text.strip()
        tag.replace_with(text)
    return soup.get_text()


def ExtractTweets():
    headers = {
        'Host': 'www.britannica.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }

    response = requests.get('https://www.britannica.com/on-this-day', headers=headers)
    result = response.text.split('<img loading="lazy" ')
    tweets = []
    for line in result:
        if '<div class="card-body font-serif">' in line:
            for data in line.splitlines():
                if 'https://cdn' in data:
                    try:
                        image_url = re.search('src="(.*)?',data)
                        image_url = image_url.group(1)
                        image_url = image_url.split('?')
                        image = requests.get(image_url[0])
                    except:
                        continue
                if 'div class="card-body font-serif' in line:
                    konten = data.split('<div class="card-body font-serif">')
                    if 'md-crosslink' in konten[0]:
                        isi = remove_tags(konten[0].split('otd-he-link font-weight-bold')[0])
                        isi = isi.replace(' —',' ').replace('—',', ').replace(' ,',',').replace('  ',' ').replace('\n','    ')
                        if image and isi:
                            tweets.append([isi,image.content])
    return tweets


account = twitter.Account(auth_token="AUTH_TOKEN_HERE")

async def main():
    async with twitter.Client(account) as twitter_client:
        source = ExtractTweets()
        sleep_time = compute_sleep_time(len(source))
        print('[+] Found ',len(source), 'Tweet Content for Today!')
        print('[+] Tweet Interval is ',int(sleep_time/60), 'Minutes')
        random.shuffle(source)
        print('[=====================================================================]')
        for content in source:
            media_id = await twitter_client.upload_image(content[1])
            tweet_id = await twitter_client.tweet('TODAY IN HISTORY! \n\n'+content[0]+'\n\nhttps://x.com/monkasalami/status/1780394355699896386',media_id=media_id)
            print('Tweet sent!, text: ', content[0][0:40],'...')
            print('    | ')
            print('    ---> Tweet ID: ', tweet_id)
            print('Sleeping for ', int(sleep_time/60), 'Minutes')
            print('[=====================================================================]')
            time.sleep(sleep_time)

asyncio.run(main())