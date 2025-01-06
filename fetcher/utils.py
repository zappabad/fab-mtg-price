import requests
import pandas as pd
import os
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings

BASE_DIR = settings.BASE_DIR

# Set up logging configuration
logger = logging.getLogger(__name__)

class TCGPlayerFetcher:
    """A class to fetch data from the TCGPlayer API."""
    def __init__(self, query, cache_duration_days=7):
        self.url = "https://mp-search-api.tcgplayer.com/v1/search/request"
        self.cache_folder = os.path.join(BASE_DIR, ".cache")
        self.query = query
        self.cache_duration_days = cache_duration_days
        self.cache_file = os.path.join(self.cache_folder, f"{self.query}_cache.json")
        self.params = {
            "q": query,
            "isList": "false",
            "mpfev": "3068"
        }
        self.payload = {
            "algorithm": "sales_dismax",
            "from": 0,
            "size": 50,
            "filters": {"term": {}, "range": {}, "match": {}},
            "listingSearch": {
                "context": {"cart": {}},
                "filters": {
                    "term": {"sellerStatus": "Live", "channelId": 0},
                    "range": {"quantity": {"gte": 1}},
                    "exclude": {"channelExclusion": 0}
                }
            },
            "context": {"cart": {}, "shippingCountry": "US", "userProfile": {}},
            "settings": {"useFuzzySearch": True, "didYouMean": {}},
            "sort": {}
        }
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
        }
        self.df = None
        self.raw_data = None

    def _is_cache_valid(self):
        """Check if the cache is still valid based on the expiration time."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                cache_timestamp = datetime.strptime(cache_data["timestamp"], "%Y-%m-%d %H:%M:%S")
                expiration_time = cache_timestamp + timedelta(days=self.cache_duration_days)
                return datetime.now() < expiration_time
        return False

    def _load_cache(self):
        """Load data from the cache file."""
        with open(self.cache_file, 'r') as f:
            cache_data = json.load(f)
            self.raw_data = cache_data["data"]
            self.df = pd.json_normalize(self.raw_data[0]['results'], max_level=1)
            self.df = self.df[self.df['productName'].str.contains(self.query, case=False, na=False)]
            self.df.sort_values('lowestPrice', ascending=True, inplace=True)


    def _save_cache(self, raw_data):
        """Save raw data to the cache file."""
        cache_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": raw_data
        }
        print(self.cache_file)
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)

    def fetch_data(self):
        """Fetch data either from cache or the API."""
        if self._is_cache_valid():
            logger.info("Loading data from cache...")
            self._load_cache()
        else:
            logger.info("Fetching fresh data from API...")
            response = requests.post(self.url, params=self.params, headers=self.headers, json=self.payload)
            response_json = response.json()
            # Save the raw JSON response to cache
            self._save_cache(response_json['results'])
            self.raw_data = response_json['results']
            self.df = pd.json_normalize(self.raw_data[0]['results'], max_level=1)
            self.df = self.df[self.df['productName'].str.contains(self.query, case=False, na=False)]
            self.df.sort_values('lowestPrice', ascending=True, inplace=True)

    def get_lowest_price(self):
        if self.df is not None:
            return self.df['lowestPrice'].min()
        return None

    def get_market_price(self):
        if self.df is not None:
            return self.df['marketPrice'].min()
        return None
    
    def get_full_data(self):
        return self.df
    
    def get_card_data(self):
        return self.df[['productLineName', 'setName', 'productName']]

    def get_lowest_price_with_shipping(self):
        if self.df is not None:
            return self.df['lowestPriceWithShipping'].min()
        return None
