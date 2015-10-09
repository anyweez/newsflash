# Newsflash backend
The Newsflash backend regularly polls a list of provided RSS feeds, fetches any articles it finds,
and labels both "major" and "minor" countries that appear as relevant in the body of the article.
## Schema
All data is stored in a single database, currently named "newsflash" though this should one day be
part of a configuration file / command line param.

The collections in the database include:

- **articles** - 
- **country_tags** - one document per country, containing a bunch of different terms that should be
mapped to that country.
- **rss** - rss feeds that should be polled for new news URL's