from flask import Flask
from flask_cors import CORS


def setup_cors(app):
    """
    Configure CORS for the Flask application

    Args:
        app (Flask): The Flask application instance
    """
    # Enable CORS for all routes
    CORS(app, resources={
        # Allow all routes
        r"/*": {
            # Allow requests from these origins
            "origins": [
                "http://localhost:3000",  # React dev server
                "http://localhost:5000",  # Flask dev server
                "https://spacelogic.yourdomain.com"  # Production domain
            ],
            # Allow credentials (cookies, authorization headers)
            "supports_credentials": True,
            # Allow these methods
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            # Allow these headers
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    return app