from imgurpython import ImgurClient
from config import client_id, client_secret, album_id, access_token, refresh_token

client = ImgurClient(client_id, client_secret, access_token, refresh_token)

if __name__ == "__main__":
    config = {
        'album': album_id,
        'name': 'test-name!',
        'title': 'test-linebot',
        'description': 'test-description'
    }
    print("Uploading image... ")
    # image = client.upload_from_path('TFT.jpg', config=config, anon=False)
    print("Done")
    '''
    for album in client.get_account_albums('me'):
        album_title = album.title if album.title else 'Untitled'
    print('Album: {0} ({1})'.format(album_title, album_id))

    for image in client.get_album_images(album_id):
        image_title = image.title if image.title else 'Untitled'
        print('\t{0}: {1}'.format(image_title, image.link))
    '''
    for image in client.get_album_images(album_id):
        image_title = image.title if image.title else 'Untitled'
    print(image.link)
    # Save some API credits by not getting all albums

