from dotenv import load_dotenv
import os

load_dotenv()

# Validate required vars are present
required_vars = [
    'POSTGRES_USER', 'POSTGRES_PW', 'POSTGRES_DB',
    'KAFKA_TOPIC', 'KAFKA_BOOTSTRAP_SERVERS',
    'WIKI_STREAM_URL', 'USER_AGENT'
]

for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Postgres
POSTGRES_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PW'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432))
}

# Kafka
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP')

# Wikipedia stream
WIKI_STREAM_URL = os.getenv('WIKI_STREAM_URL')
HEADERS = {
    "Accept": "text/event-stream",
    "User-Agent": os.getenv('USER_AGENT')
}
