import feedparser
from datetime import datetime

def get_consolidated_todays_feeds(urls):
    """
    Parse a list of XML URLs and return a consolidated list of feeds published today.

    Args:
        urls (list): A list of XML feed URLs.

    Returns:
        list: A consolidated list of entries published today.
    """
    consolidated_entries = []
    today = datetime.now().date()

    for url in urls:
        feed = feedparser.parse(url)

        # Extract items published today
        for entry in feed.entries:
            if 'published_parsed' in entry:
                published_date = datetime(*entry.published_parsed[:6]).date()
                if published_date == today:
                    # Add the entry to the consolidated list
                    consolidated_entries.append({
                        'title': entry.title,
                        'published': entry.published,
                        'link': entry.link,
                        'source': url  # Include the source URL
                    })

    return consolidated_entries

# Example usage with the provided URLs
xml_urls = [
    "https://rss.app/feeds/PfSPW1PZmIDrjC8u.xml",
    "https://rss.app/feeds/bovDvfqaIz2KoDdw.xml",
    "https://rss.app/feeds/qKjOEYXW4oEP6xYP.xml",
    "https://rss.app/feeds/56HKOZAvi3Ym1tm7.xml",
    "https://rss.app/feeds/uZLwiQhErv8b4yEK.xml",
    "https://rss.app/feeds/K2enb0duBnv1BgXn.xml",
    "https://rss.app/feeds/YqqGCKRoUgtzQxse.xml",
    "https://rss.app/feeds/AlOYwfMt50xeeAGX.xml"
]

todays_feeds = get_consolidated_todays_feeds(xml_urls)
with open("result.txt", "w") as file:
    for feed in todays_feeds:
        file.write("Title: {}\n".format(feed['title']))
        file.write("Published: {}\n".format(feed['published']))
        file.write("Link: {}\n".format(feed['link']))
        file.write("Source URL: {}\n\n".format(feed['source']))
        file.write("-" * 50 + "\n")
