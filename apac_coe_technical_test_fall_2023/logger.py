import logging

# Set the log level to INFO
logging.basicConfig(level=logging.INFO)

# Create a formatter with the desired format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
)

# Create a logger
logger = logging.getLogger(__name__)

# Create a stream handler and set the formatter
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add the stream handler to the logger
logger.addHandler(stream_handler)
