"""Main entry point for Google App Engine"""

import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get("FLASK_ENV", "production")

# Create application instance
app = create_app(config_name)

# Expose the app for Google App Engine
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))