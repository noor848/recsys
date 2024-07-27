# from confluent_kafka import Consumer, KafkaException, KafkaError
# import sys
# import json
# from river import reco, metrics, compose, linear_model, preprocessing, feature_extraction

# # Kafka Consumer configuration
# conf = {
#     'bootstrap.servers': 'localhost:9092',
#     'group.id': 'python-consumer-group',
#     'auto.offset.reset': 'earliest'
# }

# # Create Consumer instance
# consumer = Consumer(conf)

# # Subscribe to topic
# topic = 'dbserver1.public.test'
# consumer.subscribe([topic])

# # In-memory storage for video features and user interests
# video_features = {
#     '1': {'name': 'Video 1', 'labels': 'action comedy'},
#     '2': {'name': 'Video 2', 'labels': 'drama'},
#     '3': {'name': 'Video 3', 'labels': 'comedy drama'},
# }

# user_interests = {
#     '1': {'interests': 'comedy'},
#     '2': {'interests': 'drama'},
#     '3': {'interests': 'action'},
# }

# # In-memory storage for known video IDs
# known_video_ids = list(video_features.keys())

# # Define the collaborative filtering model
# collaborative_filtering = reco.FunkMF(n_factors=10)

# # Define the content-based filtering model
# content_based_filtering = compose.Pipeline(
#     feature_extraction.BagOfWords(on='labels', ngram_range=(1, 1)),
#     preprocessing.StandardScaler(),
#     linear_model.LinearRegression()
# )

# # Define the metric to evaluate the model
# metric = metrics.MAE()  # Mean Absolute Error for regression

# # Hybrid model combining collaborative filtering and content-based filtering
# class HybridModel:

#     def __init__(self, collaborative_model, content_model):
#         self.collaborative_model = collaborative_model
#         self.content_model = content_model

#     def learn_one(self, x, y):
#         self.collaborative_model.learn_one(x['user_id'], x['video_id'], y)
#         self.content_model.learn_one(x, y)
#         return self

#     def predict_one(self, x):
#         collaborative_pred = self.collaborative_model.predict_one(x['user_id'], x['video_id'])
#         content_pred = self.content_model.predict_one(x)
#         return (collaborative_pred + content_pred) / 2

# def get_top_n_recommendations(user_id, model, video_ids, n=5):
#     # Predict the score for each video
#     predictions = {
#         video_id: model.predict_one({
#             'user_id': user_id,
#             'video_id': video_id,
#             'labels': video_features.get(video_id, {}).get('labels', ''),
#             'interests': user_interests.get(user_id, {}).get('interests', '')
#         })
#         for video_id in video_ids
#     }

#     # Sort videos by predicted score in descending order and get the top-N
#     recommended_videos = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n]

#     return recommended_videos

# def consume_loop(consumer, topics):
#     try:
#         hybrid_model = HybridModel(collaborative_filtering, content_based_filtering)

#         while True:
#             msg = consumer.poll(timeout=1.0)
#             if msg is None:
#                 continue
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
#                                      (msg.topic(), msg.partition(), msg.offset()))
#                 elif msg.error():
#                     raise KafkaException(msg.error())
#             else:
#                 # Proper message
#                 message_value = msg.value().decode('utf-8')

#                 payload = json.loads(message_value)

#                 after = payload.get('payload', {}).get('after', {})
#                 print(after)
#                 user_id = str(after.get('user_id'))
#                 video_id = str(after.get('video_id'))
#                 liked = after.get('liked')

#                 ##comined both
#                 features = {
#                     'user_id': user_id,
#                     'video_id': video_id,
#                     'labels': video_features.get(video_id, {}).get('labels', ''),
#                     'interests': user_interests.get(user_id, {}).get('interests', '')
#                 }

#                 # Update the model with the new interaction ## done
#                 hybrid_model.learn_one(features, liked)

#                 # Update the metric ###both
#                 y_pred = hybrid_model.predict_one(features)
#                 metric.update(liked, y_pred)

#                 # Print the current MAE
#                 print(f'MAE: {metric.get():.2f}')

#                 # Print top-5 recommendations for the user
#                 recommendations = get_top_n_recommendations(user_id, hybrid_model, known_video_ids, n=5)
#                 recommended_video_names = [(video_features[video_id]['name'], score) for video_id, score in recommendations]
#                 print(f"Top-5 recommendations for user {user_id}: {recommended_video_names}")

#     except KeyboardInterrupt:
#         sys.stderr.write('%% Aborted by user\n')
#     finally:
#         consumer.close()

# if __name__ == '__main__':
#     consume_loop(consumer, [topic])









import redis
import json
import time
from river import linear_model, preprocessing, reco as cf
from river import metrics

# Configuration for Redis connection
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Initialize Redis connection
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Initialize content-based model components
scaler = preprocessing.StandardScaler()
regressor = linear_model.LinearRegression()

# Initialize collaborative filtering model
cf_model = cf.FunkMF(n_factors=100000)
metric = metrics.MAE()


def extract_features(interaction):
    """Extract features from the interaction data."""
    user_interests = interaction.get('interests', [])
    video_topics = interaction.get('topics', [])

    features = {**{f'user_interest_{interest}': 1 for interest in user_interests},
                **{f'video_topic_{topic}': 1 for topic in video_topics}}
    return features


def predict_combined_score(user_id, video_id, features, cf_model, regressor):
    """Predict the combined score using both content-based and collaborative filtering models."""

    # Predict using content-based model
    y_pred_content = regressor.predict_one(features)

    # Predict using collaborative filtering model
    y_pred_cf = cf_model.predict_one(user_id, video_id)

    # Combine predictions
    y_pred = (y_pred_content + y_pred_cf) / 2

    return y_pred


def predict_scores(user_id, user_interests, interactions_data, cf_model, regressor, scaler):
    """Predict scores for all videos for a user."""
    video_scores = []

    for interaction in interactions_data:
        video_id = interaction['video_id']
        features = extract_features(interaction)
        y_pred = predict_combined_score(user_id, video_id, features, cf_model, regressor)
        video_scores.append((video_id, y_pred))

    return video_scores

def get_top_n_recommendations(video_scores, n=5):
    """Get top N video recommendations."""
    unique_scores = {}
    for video_id, score in video_scores:
        if video_id not in unique_scores:
            unique_scores[video_id] = score
        else:
            # Keep the highest score if duplicate video_id is found
            unique_scores[video_id] = max(unique_scores[video_id], score)

    sorted_scores = sorted(unique_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores[:n]

while True:
    interaction = redis_client.lpop('interactions_list')
    if interaction:
        interaction = json.loads(interaction)
        user_id = interaction['user_id']
        video_id = interaction['video_id']
        liked = interaction['liked']
        user_interests = interaction['interests']

        features = extract_features(interaction) ## for content-based

        # Learn using content-based model
        regressor.learn_one(features, liked)

        # Learn using collaborative filtering model
        cf_model.learn_one(user_id, video_id, liked)

        # Predict current interaction
        y_pred = predict_combined_score(user_id, video_id, features, cf_model, regressor)

        # Update metric
        metric.update(liked, y_pred)
        print(metric)


        # Predict scores for all possible videos for the user
        interactions_data = redis_client.lrange('all_videos_list', 0, -1)
        interactions_data = [json.loads(inter) for inter in interactions_data]

        video_scores = predict_scores(user_id, user_interests, interactions_data, cf_model, regressor, scaler)
        top_5_recommendations = get_top_n_recommendations(video_scores)

        print(f'Top 5 Recommendations for User {user_id}: {top_5_recommendations}')
    else:
        time.sleep(1)















