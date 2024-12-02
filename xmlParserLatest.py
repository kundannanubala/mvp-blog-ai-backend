import feedparser
from datetime import datetime

def get_consolidated_todays_feeds(urls):
    """
    Parses a list of XML feed URLs and returns a consolidated list of feed entries published today.

    This function iterates over each provided URL, parses the XML feed, and checks each entry's 
    publication date. If the entry was published today, it is added to the consolidated list.

    Args:
        urls (list): A list of XML feed URLs to be parsed.

    Returns:
        list: A list of dictionaries, each containing details of entries published today. 
              Each dictionary includes the entry's title, publication date, link, and source URL.
    """
    consolidated_entries = []  # Initialize an empty list to store today's entries
    today = datetime.now().date()  # Get today's date for comparison

    for url in urls:
        # Parse the XML feed from the current URL
        feed = feedparser.parse(url)

        # Iterate over each entry in the feed
        for entry in feed.entries:
            # Check if the entry has a 'published_parsed' attribute
            if "published_parsed" in entry:
                # Convert the parsed publication date to a date object
                published_date = datetime(*entry.published_parsed[:6]).date()
                # Compare the entry's publication date with today's date
                if published_date == today:
                    # Add the entry to the consolidated list with relevant details
                    consolidated_entries.append(
                        {
                            "title": entry.title,  # Title of the entry
                            "published": entry.published,  # Publication date as a string
                            "link": entry.link,  # URL link to the entry
                            "source": url,  # Source URL of the feed
                        }
                    )

    return consolidated_entries  # Return the list of today's entries

# Example usage with a predefined list of XML feed URLs
xml_urls = [
    "https://rss.app/feeds/PfSPW1PZmIDrjC8u.xml",
    "https://rss.app/feeds/bovDvfqaIz2KoDdw.xml",
    "https://rss.app/feeds/qKjOEYXW4oEP6xYP.xml",
    "https://rss.app/feeds/56HKOZAvi3Ym1tm7.xml",
    "https://rss.app/feeds/uZLwiQhErv8b4yEK.xml",
    "https://rss.app/feeds/K2enb0duBnv1BgXn.xml",
    "https://rss.app/feeds/YqqGCKRoUgtzQxse.xml",
    "https://rss.app/feeds/AlOYwfMt50xeeAGX.xml",
]

# Fetch today's feeds from the provided URLs
todays_feeds = get_consolidated_todays_feeds(xml_urls)

# Write the consolidated entries to a text file
with open("result.txt", "w") as file:
    for feed in todays_feeds:
        # Write each entry's details to the file
        file.write("Title: {}\n".format(feed["title"]))
        file.write("Published: {}\n".format(feed["published"]))
        file.write("Link: {}\n".format(feed["link"]))
        file.write("Source URL: {}\n\n".format(feed["source"]))
        file.write("-" * 50 + "\n")  # Separator between entries
