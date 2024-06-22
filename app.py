import click
import os
import shutil
import json
from jinja2 import Environment, PackageLoader, select_autoescape
from dotenv import load_dotenv

import services

load_dotenv()  # take environment variables from .env.

# setup Jinja
env = Environment( loader=PackageLoader("app"), autoescape=select_autoescape())

def generateMainPage(items):

    newItems = []
    for item in items:
        if item['content'] == '':
            continue

        newItems.append( services.createItem(item) )

    template = env.get_template("home.html")
    with open("static_site/home.html", "w") as f:
        f.write(template.render(items=newItems))

def generateThreadPage(mainItem):

    item_id = mainItem["id"]

    threads_file = services.thread_file(item_id)
    if not os.path.exists(threads_file):
        return

    with open(threads_file, "r") as f:
        thread = json.load(f)

    ancestors = []
    descendants = []
    for item in thread["ancestors"]:
        ancestors.append( services.createItem(item) )

    for item in thread["descendants"]:
        descendants.append( services.createItem(item) )

    template = env.get_template("thread.html")
    file = f"static_site/thread/{item_id}.html"
    with open(file, "w") as f:
        f.write(template.render(ancestors=ancestors, mainItem=services.createItem(mainItem), descendants=descendants))

def refreshItems( full_refresh = False ):
    services.refresh_bookmarks( False, full_refresh )
    updatePages()

def updatePages():
    # Remove static_site folder
    print( "Cleaning old pages...." )
    if os.path.exists("static_site"):
        shutil.rmtree('static_site')

    # Ensure that all folders exist
    if not os.path.exists("static_site/thread"):
        os.makedirs("static_site/thread")
    if not os.path.exists("static_site/css"):
        os.makedirs("static_site/css")
        shutil.copyfile("app_data/app.css", "static_site/css/app.css")

    print( "Generating pages...." )
    with open(services.items_file, "r") as f:
        items = json.load(f)


    generateMainPage(items)

    for item in items:
        try:
            generateThreadPage(item)
        except Exception as e:
            print( f"Error generating thread {item['id']} - {e}")
            # print(traceback.format_exc())

    print( "Finished." )

@click.command()
@click.option('--use-local', is_flag=True, show_default=True, default=False, help='Just refresh the pages from cache.')
@click.option('--full-refresh', is_flag=True, show_default=True, default=False, help='Refresh all items including threads.')
def main( use_local, full_refresh ):
    if use_local:
        print( "Using local cache" )
        updatePages()
    else:
        print( "Updating items" )
        refreshItems(full_refresh)

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()  # take environment variables from .env.

    main()