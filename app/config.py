import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), 'templates')
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
