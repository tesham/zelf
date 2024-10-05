import time
from src.contents.models import Content
import requests

class TokenBucket:

    def __init__(self, tokens, time_unit, forward_callback, drop_callback):
        self.tokens = tokens
        self.time_unit = time_unit
        self.forward_callback = forward_callback
        self.drop_callback = drop_callback
        self.bucket = tokens
        self.last_check = time.time()

    def handle(self):

        content = Content.objects.get(id=1)

        d = {
            "content_id": content.id ,
            "title": content.title,
            "url": content.url,
            "author_username": content.author.username
        }

        comment_gen_url = 'https://hackapi.hellozelf.com/api/v1/ai_comment/'

        headers = {
            'x-api-key': '05825ac5sk_d10esk_42bcsk_9999sk_94c3dea310db1728067022'
        }

        res = requests.post(url=comment_gen_url, json=d, headers=headers)
        comment = dict()
        if res.status_code == 200:
            comment = res.json()
        else:
            print('error ', res.content)
            return

        post_commnent_url = 'http://localhost:8000/api/v1/comment/'

        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        self.bucket = self.bucket + \
            time_passed * (self.tokens / self.time_unit)

        if (self.bucket > self.tokens):
            self.bucket = self.tokens

        if (self.bucket < 1):
            self.drop_callback(post_commnent_url, comment)
        else:
            self.bucket = self.bucket - 1
            self.forward_callback(post_commnent_url, comment)


def forward(url, data):

    headers = {
        'x-api-key': '05825ac5sk_d10esk_42bcsk_9999sk_94c3dea310db1728067022'
    }

    res = requests.post(url=url, json=data, headers=headers)

    if res.status_code == 200:
        print(res.json())
    else:
        print('Error', res.content)

def drop(url ,data):
    print("request dropped: " + str(url) + 'data : '+ data)


throttle = TokenBucket(1, .5, forward, drop)

counter = 0
no_of_iter = 100
flag = True

while flag:

    throttle.handle()
    counter += 1

    if counter == no_of_iter:
        flag = False
