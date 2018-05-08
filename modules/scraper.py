from modules.scrapers.overgg import Overgg
from modules.scrapers.owl import OWL

class Scraper:
    @classmethod
    def scrape_match_time(cls, match):
        if 'scrape_method' in match:
            if match['scrape_method'] == 'overgg':
                return Overgg.scrape_match_time(match)
            elif match['scrape_method'] == 'owl':
                return None
        else:
            return None

    @classmethod
    def scrape_match(cls, match):
        if 'scrape_method' in match:
            if match['scrape_method'] == 'overgg':
                return Overgg.scrape_match(match)
            elif match['scrape_method'] == 'owl':
                return None
        else:
            return None

    @classmethod
    def scrape_event(cls, event):
        if 'scrape_method' in event:
            if event['scrape_method'] == 'overgg':
                return Overgg.scrape_event(event)
            elif event['scrape_method'] == 'owl':
                return None
        else:
            return None