import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Sample data
users = pd.DataFrame({
    'user_id': [1, 2, 3],
    'interests': ['sports, music', 'cooking, travel', 'tech, gaming'],
    'liked_videos': [[101, 102], [103, 104], [105, 106]]
})

videos = pd.DataFrame({
    'video_id': [101, 102, 103, 104, 105, 106],
    'title': ['Football highlights', 'Concert footage', 'Recipe for pasta', 'Travel guide to Japan', 'Latest tech news', 'Gaming tutorial'],
    'category': ['sports', 'music', 'cooking', 'travel', 'tech', 'gaming'],
    'likes': [150, 200, 50, 80, 300, 400]
})

# Process user interests
tfidf = TfidfVectorizer()
user_interests_matrix = tfidf.fit_transform(users['interests'])

# Process video titles
video_titles_matrix = tfidf.fit_transform(videos['title'])

print("User Interests Matrix:\n", user_interests_matrix.toarray())
print("Video Titles Matrix:\n", video_titles_matrix.toarray())
