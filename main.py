import redis
import json

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Diverse interaction data
interaction_data = [
    {'user_id': 1, 'video_id': '1', 'liked': 1, 'interests': ['technology', 'education']},
    {'user_id': 2, 'video_id': '1', 'liked': 0, 'interests': ['sports', 'movies']},
    {'user_id': 1, 'video_id': '2', 'liked': 1, 'interests': ['technology', 'ai']},
    {'user_id': 3, 'video_id': '2', 'liked': 0, 'interests': ['sports', 'education']},
    {'user_id': 4, 'video_id': '3', 'liked': 1, 'interests': ['soccer', 'documentaries']},
    {'user_id': 5, 'video_id': '3', 'liked': 0, 'interests': ['basketball', 'movies']},
    {'user_id': 6, 'video_id': '4', 'liked': 1, 'interests': ['soccer', 'technology']},
    {'user_id': 2, 'video_id': '4', 'liked': 0, 'interests': ['concerts', 'education']},
    {'user_id': 7, 'video_id': '1', 'liked': 1, 'interests': ['movies', 'technology']},
    {'user_id': 8, 'video_id': '2', 'liked': 0, 'interests': ['education', 'ai']},
    {'user_id': 9, 'video_id': '3', 'liked': 1, 'interests': ['documentaries', 'basketball']},
    {'user_id': 10, 'video_id': '4', 'liked': 0, 'interests': ['technology', 'sports']},
    {'user_id': 11, 'video_id': '1', 'liked': 1, 'interests': ['technology', 'ai']},
    {'user_id': 12, 'video_id': '2', 'liked': 0, 'interests': ['education', 'movies']},
    {'user_id': 13, 'video_id': '3', 'liked': 1, 'interests': ['soccer', 'documentaries']},
    {'user_id': 14, 'video_id': '4', 'liked': 0, 'interests': ['technology', 'sports']},
    {'user_id': 15, 'video_id': '1', 'liked': 1, 'interests': ['movies', 'education']},
    {'user_id': 16, 'video_id': '2', 'liked': 0, 'interests': ['ai', 'education']},
    {'user_id': 17, 'video_id': '3', 'liked': 1, 'interests': ['documentaries', 'basketball']},
    {'user_id': 18, 'video_id': '4', 'liked': 0, 'interests': ['sports', 'technology']},
    {'user_id': 19, 'video_id': '1', 'liked': 1, 'interests': ['technology', 'education']},
    {'user_id': 20, 'video_id': '2', 'liked': 0, 'interests': ['movies', 'ai']},
    {'user_id': 21, 'video_id': '3', 'liked': 1, 'interests': ['soccer', 'documentaries']},
    {'user_id': 22, 'video_id': '4', 'liked': 0, 'interests': ['sports', 'education']},
    {'user_id': 23, 'video_id': '1', 'liked': 1, 'interests': ['technology', 'movies']},
    {'user_id': 24, 'video_id': '2', 'liked': 0, 'interests': ['ai', 'education']},
    {'user_id': 25, 'video_id': '3', 'liked': 1, 'interests': ['documentaries', 'basketball']},
    {'user_id': 26, 'video_id': '4', 'liked': 0, 'interests': ['sports', 'technology']},
]

# Diverse video data
all_videos_data = [
    {'video_id': '1', 'topics': ['soccer', 'movies']},
    {'video_id': '2', 'topics': ['ai', 'education']},
    {'video_id': '3', 'topics': ['basketball', 'documentaries']},
    {'video_id': '4', 'topics': ['sports', 'technology']},
]
redis_client.delete('interactions_list')
redis_client.delete('all_videos_list')

# Insert interaction data into Redis
for interaction in interaction_data:
    redis_client.rpush('interactions_list', json.dumps(interaction))

# Insert all possible video data into Redis
for video in all_videos_data:
    redis_client.rpush('all_videos_list', json.dumps(video))

print("Data insertion complete.")
