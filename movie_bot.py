import os  
import tweepy  
import requests  
import random  
import time  
import logging  
from dotenv import load_dotenv  

# Load environment variables  
load_dotenv()  

# Konfigurasi logging  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s: %(message)s',  
    handlers=[  
        logging.FileHandler('movie_bot_debug.log', encoding='utf-8'),  
        logging.StreamHandler()  
    ]  
)  

class MovieTwitterBot:  
    def __init__(self):  
        # Ambil kredensial dari environment variables  
        twitter_credentials = {  
            'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),  
            'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),  
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),  
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')  
        }  
        omdb_api_key = os.getenv('OMDB_API_KEY')  

        # Validasi kredensial  
        self._validate_credentials(twitter_credentials, omdb_api_key)  

        # Inisialisasi Twitter client  
        self.client = tweepy.Client(  
            consumer_key=twitter_credentials['consumer_key'],  
            consumer_secret=twitter_credentials['consumer_secret'],  
            access_token=twitter_credentials['access_token'],  
            access_token_secret=twitter_credentials['access_token_secret']  
        )  
        self.omdb_api_key = omdb_api_key  

        # Verifikasi kredensial Twitter  
        try:  
            user_info = self.client.get_me()  
            logging.info(f"Authenticated as: {user_info.data.username}")  
        except Exception as e:  
            logging.error(f"Authentication failed: {e}")  
            raise  

    def _validate_credentials(self, credentials, api_key):  
        """Validasi keberadaan kredensial"""  
        missing_credentials = [  
            key for key, value in credentials.items()   
            if not value  
        ]  
        
        if missing_credentials or not api_key:  
            error_msg = f"Missing credentials: {missing_credentials}"  
            if not api_key:  
                error_msg += ", OMDB API Key"  
            logging.critical(error_msg)  
            raise ValueError(error_msg)  

    def fetch_random_movie(self):  
        """Ambil film acak dari OMDb API"""  
        keywords = [  
            'action', 'comedy', 'drama', 'thriller', 'horror',   
            'romance', 'sci-fi', 'fantasy', 'animation', 'crime'  
        ]  
        
        search_keyword = random.choice(keywords)  
        
        try:  
            # Cari film berdasarkan keyword  
            search_url = f"http://www.omdbapi.com/?s={search_keyword}&apikey={self.omdb_api_key}"  
            search_response = requests.get(search_url, timeout=10)  
            
            if search_response.status_code == 200:  
                movie_data = search_response.json()  
                
                if movie_data.get('Response') == 'True' and movie_data.get('Search'):  
                    # Pilih film acak dari hasil pencarian  
                    selected_movie = random.choice(movie_data['Search'])  
                    
                    # Ambil detail film  
                    detail_url = f"http://www.omdbapi.com/?i={selected_movie['imdbID']}&apikey={self.omdb_api_key}"  
                    detail_response = requests.get(detail_url, timeout=10)  
                    
                    if detail_response.status_code == 200:  
                        movie_details = detail_response.json()  
                        
                        return {  
                            'title': movie_details['Title'],  
                            'description': movie_details['Plot'],  
                            'url': f"https://www.imdb.com/title/{movie_details['imdbID']}/",  
                            'rating': movie_details.get('imdbRating', 'N/A'),  
                            'year': movie_details['Year']  
                        }  
            
            logging.warning(f"No movies found for keyword: {search_keyword}")  
            return None  
        
        except requests.exceptions.RequestException as e:  
            logging.error(f"Network error while fetching movie: {e}")  
            return None  
        except Exception as e:  
            logging.error(f"Unexpected error in fetch_random_movie: {e}")  
            return None  

    def tweet_random_movie(self):  
        """Tweet film rekomendasi"""  
        movie = self.fetch_random_movie()  
        if movie:  
            try:  
                tweet_text = (  
                    f"🎬 Movie Recommendation 🍿\n\n"  
                    f"📽️ {movie['title']} ({movie['year']})\n\n"  
                    f"⭐ Rating: {movie['rating']}/10\n\n"  
                    f"📝 {movie['description'][:250]}...\n\n"  
                    f"🔗 {movie['url']}\n\n"  
                    f"#MovieRecommendation #WatchTonight"  
                )  
                
                response = self.client.create_tweet(text=tweet_text)  
                logging.info(f"Successfully tweeted movie: {movie['title']}")  
                return True  
            
            except Exception as e:  
                logging.error(f"Error while tweeting: {e}")  
                return False  
        return False  

def main():  
    try:  
        # Ambil interval tweet dari environment (default 1 jam)  
        tweet_interval = int(os.getenv('TWEET_INTERVAL', 3600))  
        
        bot = MovieTwitterBot()  
        
        logging.info("🤖 Movie Twitter Bot started!")  
        
        # Loop utama  
        while True:  
            try:  
                bot.tweet_random_movie()  
                time.sleep(tweet_interval)  
            
            except Exception as inner_error:  
                logging.error(f"Error in main loop: {inner_error}")  
                time.sleep(tweet_interval)  
    
    except Exception as e:  
        logging.critical(f"Critical error in main: {e}")  

if __name__ == "__main__":  
    main()