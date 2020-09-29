import json

import google_auth_oauthlib
import requests
from datetime import date

import googleapiclient.discovery
import googleapiclient.errors

from textgenrnn import textgenrnn

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

apiKey = "<Your API Key>"
videoID = "<Your Video ID>"


def main(auth_tokens):
    print("Getting YT Data...")
    get_yt_data()
    print("Generating video content...")
    gen_new_data(auth_tokens)
    print("Done!")


def get_yt_data():
    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=apiKey)

    titles = open("titles.txt", "wb")
    desc = open("descriptions.txt", "wb")
    tags = open("tags.txt", "wb")

    page_token = ""

    while True:
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="US",
            maxResults=10000,
            pageToken=page_token
        )
        response = request.execute()

        for vid in response['items']:
            titles.write((vid['snippet']['title'] + "\n").encode('utf-8'))
            desc_to_add = (vid['snippet']['description'].replace("\r", " ").replace("\n", " ").strip()).encode('utf-8')
            if desc_to_add:
                desc.write(desc_to_add)
                desc.write("\n".encode('utf-8'))
            if 'tags' in vid['snippet']:
                for tag in vid['snippet']['tags']:
                    tags.write((tag + "\n").encode('utf-8'))

        if 'nextPageToken' not in response:
            break
        else:
            page_token = response['nextPageToken']

    titles.close()
    desc.close()
    tags.close()


def gen_new_data(auth_tokens):
    textgen = textgenrnn()
    textgen.train_from_file('titles.txt', num_epochs=2)
    title = textgen.generate(1, temperature=0.2, progress=False, return_as_list=True)
    vid_title = title[0]

    textgen.reset()
    textgen.train_from_file('descriptions.txt', delim="\n", num_epochs=1)
    desc = textgen.generate(1, temperature=0.2, progress=False, return_as_list=True)
    vid_desc = desc[0]

    textgen.reset()
    textgen.train_from_file('tags.txt', delim="\n", num_epochs=1)
    tags = textgen.generate(50, temperature=0.2, progress=False, return_as_list=True)

    print("The title created: " + vid_title)
    print("The desc created: " + vid_desc)
    print("The tags created: " + ', '.join(tags))

    # Youtube only allows a max of 5000 characters max for the description
    if len(vid_desc) > 5000:
        vid_desc = vid_desc[0:5000]

    # Youtube only allows a max of 100 characters max for the title
    if len(vid_title) > 100:
        vid_title = vid_title[0:100]

    # Youtube only allows a max of 500 characters max for tags
    i = 0
    j = 0
    while i < len(tags) and j < 500:
        j += len(tags[i])
        i += 1

    if j > 500:
        tags = tags[0:i]

    update_video(vid_title, vid_desc, tags, auth_tokens)

    history = open("history.txt", "a")
    history.write(date.today().strftime("%m/%d/%y") + " \n")
    history.write("\tTitle: " + str(vid_title.encode("UTF-8", errors='replace')) + " \n")
    history.write("\tDescription: " + str(vid_desc.encode("UTF-8", errors='replace')) + " \n")
    history.write("\tTags: " + ', '.join(tags) + " \n")
    history.close()


def update_video(title, desc, tags, auth_tokens):
    if not send_video_update(title, desc, tags, auth_tokens[0]):
        secret_file = open("SECRET.json", "r")
        secret_json = json.loads(secret_file.read())
        auth_tokens[0] = update_access_token(auth_tokens[1], secret_json)
        if auth_tokens[0] is not None:
            tokens_file = open("tokens.txt", "w")
            tokens_file.write(auth_tokens[0] + "\n" + auth_tokens[1])
            tokens_file.close()
            send_video_update(title, desc, tags, auth_tokens[0])


def send_video_update(title, desc, tags, token):
    response = requests.put(
        'https://www.googleapis.com/youtube/v3/videos?part=snippet',
        data=json.dumps({
            "id": videoID,
            "snippet": {
                "defaultLanguage": "en",
                "title": title,
                "description": desc,
                "tags": tags,
                "categoryId": "28"
            }
        }),
        headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                 "Content-Type": "application/json"})

    print(response.content)

    if response.status_code == 401:
        return False
    return True


def update_access_token(refresh_token, g_json):
    response = requests.post('https://www.googleapis.com/oauth2/v4/token',
                             params={
                                 "grant_type": "refresh_token",
                                 "client_id": g_json['installed']['client_id'],
                                 "client_secret": g_json['installed']['client_secret'],
                                 "refresh_token": refresh_token
                             })

    if response.ok:
        return response.json()['access_token']
    else:
        return None


if __name__ == "__main__":
    f = open("tokens.txt", "r")
    tokens = f.read().split("\n")
    f.close()

    if len(tokens) != 2:
        # We need to get authentication tokens!
        # Youtube doesn't have a true headless way to do this :(
        # so sadly you have to run this once to get the access and refresh tokens.
        # After this, we should bea able to use re refresh token to get new access tokens for a while...

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file("SECRET.json", scopes)
        credentials = flow.run_console()
        tokens = [credentials.token, credentials.refresh_token]
        f = open("tokens.txt", "w")
        f.write(tokens[0] + "\n" + tokens[1])
        f.close()
    main(tokens)
