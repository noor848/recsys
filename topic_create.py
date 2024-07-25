from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

def create_topic(bootstrap_servers, topic_name, num_partitions=1, replication_factor=1):
    admin_client = KafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        client_id='topic-creator'
    )

    topic_list = []
    topic_list.append(NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor))

    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{topic_name}' created successfully.")
    except TopicAlreadyExistsError:
        print(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        print(f"Failed to create topic '{topic_name}': {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    bootstrap_servers = 'localhost:9092'  # Update with your Kafka bootstrap servers if different
    topic_name = 'dbserver1.public.test'  # Update with the desired topic name

    create_topic(bootstrap_servers, topic_name)
