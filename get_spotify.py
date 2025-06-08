from spotify_login import authenticate
import requests

import cv2

if __name__ == "__main__":
  tokens = authenticate()
  access_token = tokens.get('access_token')
  refresh_token = tokens.get('refresh_token')
  
  response = requests.get(
    'https://api.spotify.com/v1/me',
    headers={
      'Authorization': f'Bearer {access_token}'
  })
  
  info = response.json()
  res = requests.get(
    info['images'][0]['url'],
    headers={
      'Authorization': f'Bearer {access_token}'
  })
  
  with open('profile_picture.jpg', 'wb') as f:
    f.write(res.content)

  cv2.imshow('Profile Picture', cv2.imread('profile_picture.jpg'))
  
  cv2.waitKey(0)
  cv2.destroyAllWindows()