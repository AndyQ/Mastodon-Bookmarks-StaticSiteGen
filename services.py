import json
import os
from mastodon import Mastodon

cache_folder = "./cache"
last_id_file = f"{cache_folder}/last_id.txt"
items_file = f"{cache_folder}/items.json"

def thread_file( item_id ):
    return f"{cache_folder}/{item_id}.json"

def createItem( item ):
    content = item["content"].replace('class="invisible"', "").replace('class="ellipsis"', "")
    url = ""
    title = "No title"
    hasThreads = False
    image = None

    display_name = item["account"]["display_name"]
    account_name = item["account"]["acct"]

    card = item.get('card', None)
    if card != None:
        title = card.get('title', "")
        url = card.get('url', "")
        image = card.get('image', None)
    else:
        if item.get("spoiler_text", "") != "":
            title = item.get("spoiler_text", "")

    if image == None or image == "":
        if len(item.get('media_attachments', [])) > 0:
            image = item.get('media_attachments', [])[0].get('preview_url', "")

    # If thread exists, add to list
    if os.path.exists( thread_file(item["id"])):
        hasThreads = True
        
    ret = {"item_id": f"{item['id']}", "display_name" : display_name, "account_name" : account_name, "title": title, "content": content, "link": url, "image" : image, "has_threads": hasThreads}
    return ret


def get_mastodon_client():
    access_token = os.environ['MASTODON_ACCESS_TOKEN']
    mastodon = Mastodon(
        access_token = access_token,
        api_base_url = 'https://mastodon.social'
    )
    return mastodon

def get_status_thread( mastodon, status_id, full_refresh = False ):
    file_name = thread_file(status_id)

    if os.path.exists(file_name) and not full_refresh:
        print( f"   Thread {status_id} already exists" )
        return
    
    statuses = mastodon.status_context( status_id )
    with open(file_name, "w") as f:
        json.dump(statuses, f, indent=4, default=str)

def refresh_item(status_id, full_refresh = False,  mastodon = None):
    if mastodon == None:
        mastodon = get_mastodon_client()
    
    print( f"Retrieving threads for {status_id}")
    try:
        get_status_thread( mastodon, status_id, full_refresh )

        filename = thread_file(status_id)
        with open(filename, "r") as f:
            statuses = json.load(f)

        if len(statuses["descendants"]) == 0 and len(statuses["ancestors"]) == 0:
            os.remove( filename )
    except Exception as e:
        print( f"    *** Error retrieving thread {status_id} - {e}")


def refresh_bookmarks( local = False, full_refresh = False):

    # ensure threads folder exists
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)

    #   Set up Mastodon
    mastodon = get_mastodon_client()

    # get last_id from file
    last_id = "0"
    try:
        pass
        with open(last_id_file, "r") as f:
            last_id = f.read()
    except:
        print( "No last id found" )

    # load items from file
    items = []
    if local:
        with open(items_file, "r") as f:
            items = json.load(f)
    else:
        print( "Downloading bookmarks.", end="")
        items = mastodon.bookmarks( )
        if len(items) == 0:
            print( "No new items" )
            return
        
        # Process each page
        next_items = items
        while( next_items != None and len(next_items) > 0):
            print( ".",end="", flush=True )
            next_items = mastodon.fetch_next(next_items)
            if next_items != None and len(next_items) > 0:
                items.extend( next_items )
        print("")
        # save items dict to file
        with open(items_file, "w") as f:
            json.dump(items, f, indent=4, default=str)

    max_id = 0
    for item in items:
        if not full_refresh and item['id'] <= int(last_id):
            continue

        refresh_item( item['id'], full_refresh, mastodon)
        if item['id'] > max_id:
            max_id = item['id']

    if max_id == 0:
        max_id = last_id

    #save last_id to file
    with open(last_id_file, "w") as f:
        f.write(f"{max_id}")


