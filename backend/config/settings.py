import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
FLASK_PORT = int(os.getenv('PORT', 5000))
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# News sources configuration
NEWS_SOURCES = {
    'politics': [
        'https://www.npr.org/sections/politics/',
        'https://apnews.com/politics'
    ],
    'sports': [
        'https://www.espn.com/espn/rss/news',
        'https://www.cbssports.com/',
        'https://sports.yahoo.com/'
    ],
    'business': [
        'https://www.reuters.com/business/',
        'https://www.marketwatch.com/',
        'https://finance.yahoo.com/'
    ],
    'arts': [
        'https://www.npr.org/sections/arts/',
        'https://www.theguardian.com/artanddesign',
        'https://www.artforum.com/news'
    ],
    'earth': [
        'https://www.nationalgeographic.com/environment/',
        'https://www.sciencedaily.com/news/earth_climate/',
        'https://www.bbc.com/future-planet'
    ],
    'technology': [
        'https://www.wired.com/tag/technology/',
        'https://www.theverge.com/tech',
        'https://arstechnica.com/'
    ]
}

# Scraping Configuration
# Scraping Configuration - REDUCED DELAYS
SCRAPING_DELAY_MIN = 0.1  # Reduced from 1 second
SCRAPING_DELAY_MAX = 0.2  # Reduced from 3 seconds
SCRAPING_TIMEOUT = 15
MAX_HEADLINES_PER_SOURCE = 1
MAX_HEADLINES_PER_CATEGORY = 30

