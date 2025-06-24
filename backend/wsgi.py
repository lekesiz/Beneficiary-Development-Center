"""WSGI entry point for the application."""
import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create application instance
app = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )