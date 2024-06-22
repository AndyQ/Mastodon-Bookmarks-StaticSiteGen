# mastodon-bookmarks - Static Site Generator

This app generates a set of webpages consisting of all your saved bookmarks and also the associated replies (and what your bookmark replied to if applicable)

## Installation

To run, you need python 3.12 (possibly other versions may work but not tested)

1. Create virtual env and install dependancies:  
```
python -m venv ./venv
. ./bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Set environment
Copy `.env.dist` to `.env`

Create a Mastodon access token
- Login to your Mastodon instance, ie. https://mastodon.social
- Go to Preference -> Development, click on New Application.
- Enter the name of the Application and modify the scopes required.  
Recommended scopes are:  
read:bookmarks  
read:statuses
- Submit it then click on the name of the Application you've just created.  
You'll be able to copy the Access Token here.

Copy the `.env.dist` file to `.env`

Edit the `.env` file and set the MASTODON_ACCESS_TOKEN to your generated token

## Generating the site contents

Run the application using:
```
python app.py [--use-local] [-full-refresh]
```

By default, the app will download and just update any new favourites saved since the last update.

You can use the following flags to adjust the behaviour.

use-local : Just refreshes the pages using the internal cache
full-refresh :  Does a full refresh of all the threads


The application will create a couple of folders: 
- cache - this contains the cached json data from Mastodon
- static_site - this contains the generated static site

## Viewing the generated site

To view the static site, you probably want to deploy it to a http server. 

This is outside the scope of this site BUT if you want to preview it locally,
you can run the build in python http.server:

```
cd static_site
python -m http.server
```

Then access the site through your browser on <a target="_blank" href="http://localhost:8000">http://localhost:8000</a>
