from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import json
from river import reco, metrics, compose, linear_model, preprocessing, feature_extraction

# Kafka Consumer configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'python-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Create Consumer instance
consumer = Consumer(conf)

# Subscribe to topic
topic = 'dbserver1.public.test'
consumer.subscribe([topic])

# In-memory storage for video features and user interests
video_features = {
    '1': {'name': 'Video 1', 'labels': 'action comedy'},
    '2': {'name': 'Video 2', 'labels': 'drama'},
    '3': {'name': 'Video 3', 'labels': 'comedy drama'},
}

user_interests = {
    '1': {'interests': 'comedy'},
    '2': {'interests': 'drama'},
    '3': {'interests': 'action'},
}

# In-memory storage for known video IDs
known_video_ids = list(video_features.keys())

# Define the collaborative filtering model
collaborative_filtering = reco.FunkMF(n_factors=10)

# Define the content-based filtering model
content_based_filtering = compose.Pipeline(
    feature_extraction.BagOfWords(on='labels', ngram_range=(1, 1)),
    preprocessing.StandardScaler(),
    linear_model.LinearRegression()
)

# Define the metric to evaluate the model
metric = metrics.MAE()  # Mean Absolute Error for regression

# Hybrid model combining collaborative filtering and content-based filtering
class HybridModel:

    def __init__(self, collaborative_model, content_model):
        self.collaborative_model = collaborative_model
        self.content_model = content_model

    def learn_one(self, x, y):
        self.collaborative_model.learn_one(x['user_id'], x['video_id'], y)
        self.content_model.learn_one(x, y)
        return self

    def predict_one(self, x):
        collaborative_pred = self.collaborative_model.predict_one(x['user_id'], x['video_id'])
        content_pred = self.content_model.predict_one(x)
        return (collaborative_pred + content_pred) / 2

def get_top_n_recommendations(user_id, model, video_ids, n=5):
    # Predict the score for each video
    predictions = {
        video_id: model.predict_one({
            'user_id': user_id,
            'video_id': video_id,
            'labels': video_features.get(video_id, {}).get('labels', ''),
            'interests': user_interests.get(user_id, {}).get('interests', '')
        })
        for video_id in video_ids
    }

    # Sort videos by predicted score in descending order and get the top-N
    recommended_videos = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:n]

    return recommended_videos

def consume_loop(consumer, topics):
    try:
        hybrid_model = HybridModel(collaborative_filtering, content_based_filtering)

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Proper message
                message_value = msg.value().decode('utf-8')

                payload = json.loads(message_value)

                after = payload.get('payload', {}).get('after', {})
                print(after)
                user_id = str(after.get('user_id'))
                video_id = str(after.get('video_id'))
                liked = after.get('liked')

                ##comined both
                features = {
                    'user_id': user_id,
                    'video_id': video_id,
                    'labels': video_features.get(video_id, {}).get('labels', ''),
                    'interests': user_interests.get(user_id, {}).get('interests', '')
                }

                # Update the model with the new interaction ## done
                hybrid_model.learn_one(features, liked)

                # Update the metric ###both
                y_pred = hybrid_model.predict_one(features)
                metric.update(liked, y_pred)

                # Print the current MAE
                print(f'MAE: {metric.get():.2f}')

                # Print top-5 recommendations for the user
                recommendations = get_top_n_recommendations(user_id, hybrid_model, known_video_ids, n=5)
                recommended_video_names = [(video_features[video_id]['name'], score) for video_id, score in recommendations]
                print(f"Top-5 recommendations for user {user_id}: {recommended_video_names}")

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')
    finally:
        consumer.close()

if __name__ == '__main__':
    consume_loop(consumer, [topic])
