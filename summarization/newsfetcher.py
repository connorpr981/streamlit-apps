from dotenv import load_dotenv
import json
import requests
import pandas as pd
import re
import os
from IPython.display import Markdown, display
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, ticker, num_articles, subscription_key=None):
        load_dotenv()
        self.subscription_key = subscription_key or os.getenv("AZURE_SEARCH_KEY")
        self.ticker = ticker
        self.search_url = "https://api.bing.microsoft.com/v7.0/news/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        self.num_articles = num_articles
        if self.num_articles > 100:
            self.params = {
                "q": ticker,
                "cc": "US",
                # "category": "Business",
                "count": 100,
                "freshness": "Month",
                "mkt": "en-US",
                "offset": 0,
                "originalImg": True,
                "safeSearch": "Off",
                "setLang": "en-US",
                "sortBy": "Date",
                "textDecorations": True,
                "textFormat": "HTML"
            }
        else:
            self.params = {
                "q": ticker,
                "cc": "US",
                # "category": "Business",
                "count": num_articles,
                "freshness": "Month",
                "mkt": "en-US",
                "offset": 0,
                "originalImg": True,
                "safeSearch": "Off",
                "setLang": "en-US",
                "sortBy": "Date",
                "textDecorations": True,
                "textFormat": "HTML"
            }
        self.articles_df = pd.DataFrame()

    def fetch_news_bing(self):
        all_articles = []
        for offset in range(0, self.num_articles, 100):
            self.params['offset'] = offset
            try:
                response = requests.get(self.search_url, headers=self.headers, params=self.params)
                response.raise_for_status()
                search_results = response.json()
                all_articles.extend(search_results["value"])
                if len(search_results["value"]) < 100:
                    break  # Break the loop if fewer than 100 articles are returned
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 401:
                    logger.error("401 Unauthorized error. Check your subscription key.")
                    return pd.DataFrame()
                logger.error(f"HTTP error occurred: {http_err}")
            except Exception as err:
                logger.error(f"Error occurred: {err}")
        return pd.DataFrame(all_articles)  # Combine all articles into a DataFrame

    @staticmethod
    def get_article_text(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)  # Set the read timeout to 5 seconds
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            return " ".join([paragraph.get_text() for paragraph in paragraphs])
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred for URL {url}. Skipping.")
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                logger.error(f"401 Unauthorized error for URL {url}. Skipping.")
            else:
                logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logger.error(f"Error occurred: {err}")
        return ""

    @staticmethod
    def clean_text(raw):
        text = BeautifulSoup(raw, 'html.parser').get_text().strip().lower()
        cleaned_lines = [line for line in text.split('\n') if len(line) >= 50]
        cleaned_text = '\n'.join(cleaned_lines)
        pattern = re.compile(r'(related articles.*)', re.IGNORECASE)
        match = pattern.search(cleaned_text)
        if match:
            cleaned_text = cleaned_text[:match.start()].strip()
        return cleaned_text

    def fetch_article_texts(self, articles_df):
        print(articles_df.columns)
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_to_url = {executor.submit(self.get_article_text, url): url for url in articles_df['url']}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    logger.error(f"Error fetching text for {url}: {exc}")
                    data = ""
                articles_df.loc[articles_df['url'] == url, 'text'] = data

    def run(self):
        logger.info("Fetching news from Bing News API")
        bing_articles_df = self.fetch_news_bing()
        logger.info(f"Fetched {len(bing_articles_df)} articles from Bing News API")

        combined_df = bing_articles_df.drop_duplicates(subset=['url']).reset_index(drop=True)
        
        logger.info("Fetching full text for articles")
        self.fetch_article_texts(combined_df)
        
        logger.info("Cleaning article texts")
        combined_df['text'] = combined_df['text'].apply(self.clean_text)
        
        self.articles_df = combined_df
        logger.info(f"Fetched and processed a total of {len(self.articles_df)} articles")
