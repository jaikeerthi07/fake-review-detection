import requests

APIFY_TOKEN = 'YOUR_APIFY_TOKEN_HERE'
RUN_ID = 'uXdkLfAflqVLYAjYI'

def get_log():
    url = f'https://api.apify.com/v2/actor-runs/{RUN_ID}/log?token={APIFY_TOKEN}'
    response = requests.get(url)
    print(response.text)

if __name__ == '__main__':
    get_log()
