import requests
from src.contentapi.celery import app

@app.task(queue="content_pull")
def pull_and_store_content():
    # TODO: The design of this celery task is very weird. It's posting the response to localhost:3000.
    #  which is not ideal
    url = "https://hackapi.hellozelf.com/api/v1/contents/"
    api_url = "http://localhost:3000/api/contents/"
    headers = {
        'x-api-key': '05825ac5sk_d10esk_42bcsk_9999sk_94c3dea310db1728067022'
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        res = res.json()
        for item in res:
            payload = {**item}
            requests.post(api_url, json=payload)
    else:
        print('Error occur', res.content)