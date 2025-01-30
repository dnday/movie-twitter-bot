# Gunakan base image Python resmi  
FROM python:3.11-slim  

# Set working directory  
WORKDIR /app  

# Copy requirements file  
COPY requirements.txt .  

# Install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# Copy seluruh project  
COPY . .  

# Set environment variables default  
ENV TWITTER_CONSUMER_KEY=""  
ENV TWITTER_CONSUMER_SECRET=""  
ENV TWITTER_ACCESS_TOKEN=""  
ENV TWITTER_ACCESS_TOKEN_SECRET=""  
ENV OMDB_API_KEY=""  
ENV TWEET_INTERVAL=3600  

# Jalankan script  
CMD ["python", "main.py"]