from urllib.parse import urlsplit
import requests

object_urls = [
  'https://horriblebucket.s3.us-east-2.amazonaws.com/data/artist_alias.txt',
  'https://horriblebucket.s3.us-east-2.amazonaws.com/data/artist_data.txt',
  'https://horriblebucket.s3.us-east-2.amazonaws.com/data/user_artist_data.txt'
]

def download():
  for object_url in object_urls:
    path = urlsplit(object_url).path
    fname = path.split('/')[-1]
    print(f'downloading {fname} from {object_url}')

    response = requests.get(object_url)
    with open(fname, 'wb') as f:
      f.write(response.content)

if __name__ == '__main__':
  download()