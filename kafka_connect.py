import requests
import json

# Define the connector configuration
connector_config = {
    "name": "public-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "postgres",
        "database.port": "5432",
        "database.user": "postgres",
        "database.password": "postgres",
        "database.dbname": "postgres",
        "database.server.name": "dbserver1",
        "table.include.list": "public.test",
        "name": "public-connector"
    }
}

# Kafka Connect REST API endpoint
kafka_connect_url = "http://localhost:8083/connectors"

# Register the connector
response = requests.post(
    kafka_connect_url,
    headers={"Content-Type": "application/json"},
    data=json.dumps(connector_config)
)

if response.status_code == 201:
    print("Connector created successfully.")
else:
    print("Failed to create connector.")
    print("Status code:", response.status_code)
    print("Response:", response.json())
