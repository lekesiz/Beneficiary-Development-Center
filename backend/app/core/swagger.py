"""
Swagger/OpenAPI configuration for the BDC API.
"""

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint, jsonify, render_template_string


# Create the APISpec instance
spec = APISpec(
    title="BDC (Beneficiary Development Center) API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
    info={
        "description": "API for managing beneficiaries, programs, courses, and evaluations in the Beneficiary Development Center platform.",
        "contact": {"email": "support@bdc.com"},
        "license": {"name": "Proprietary"},
    },
    servers=[
        {"url": "http://localhost:5000", "description": "Development server"},
        {"url": "https://api.bdc.com", "description": "Production server"},
    ],
)

# Security schemes
spec.components.security_scheme(
    "bearerAuth",
    {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
    },
)

# Add global security requirement
spec.options["security"] = [{"bearerAuth": []}]

# Define common responses
spec.components.response(
    "UnauthorizedError",
    {
        "description": "Access token is missing or invalid",
        "content": {
            "application/json": {
                "schema": {"type": "object", "properties": {"message": {"type": "string", "example": "Unauthorized"}}}
            }
        },
    },
)

spec.components.response(
    "NotFoundError",
    {
        "description": "The specified resource was not found",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {"message": {"type": "string", "example": "Resource not found"}},
                }
            }
        },
    },
)

spec.components.response(
    "ValidationError",
    {
        "description": "Validation error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Validation error"},
                        "errors": {
                            "type": "object",
                            "additionalProperties": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            }
        },
    },
)

# Define common schemas
spec.components.schema(
    "Error",
    {
        "type": "object",
        "properties": {
            "error": {"type": "string", "description": "Error message"},
            "message": {"type": "string", "description": "Detailed error message"},
        },
    },
)

spec.components.schema(
    "User",
    {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "User ID"},
            "email": {"type": "string", "format": "email", "description": "User email"},
            "first_name": {"type": "string", "description": "First name"},
            "last_name": {"type": "string", "description": "Last name"},
            "full_name": {"type": "string", "description": "Full name"},
            "role": {"type": "string", "description": "User role", "enum": ["admin", "manager", "trainer", "user"]},
            "tenant_id": {"type": "integer", "description": "Tenant ID"},
            "is_active": {"type": "boolean", "description": "Whether user is active"},
            "created_at": {"type": "string", "format": "date-time", "description": "Creation timestamp"},
        },
    },
)

# Create documentation blueprint
docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/api/v1/swagger.json")
def swagger_json():
    """
    Serve the OpenAPI specification as JSON.
    """
    return jsonify(spec.to_dict())


@docs_bp.route("/api/v1/docs")
def swagger_ui():
    """
    Serve the Swagger UI for API documentation.
    """
    swagger_ui_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>BDC API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
        <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.9.0/favicon-32x32.png" sizes="32x32" />
        <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.9.0/favicon-16x16.png" sizes="16x16" />
        <style>
            html {
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }
            *, *:before, *:after {
                box-sizing: inherit;
            }
            body {
                margin: 0;
                background: #fafafa;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" charset="UTF-8"></script>
        <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
        <script>
            window.onload = function() {
                window.ui = SwaggerUIBundle({
                    url: "/api/v1/swagger.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    validatorUrl: null,
                    tryItOutEnabled: true,
                    supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                    onComplete: function() {
                        console.log("Swagger UI loaded successfully");
                    }
                });
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(swagger_ui_template)


def init_swagger(app):
    """
    Initialize Swagger/OpenAPI documentation for the Flask app.

    Args:
        app: Flask application instance
    """
    # Register the documentation blueprint
    app.register_blueprint(docs_bp)

    # Auto-discover and register API endpoints
    with app.test_request_context():
        # Import all API modules to ensure they are loaded
        from app.api.v1 import auth, beneficiaries, programs, courses, evaluations
        from app.api.v1 import users, ai
        from app.api import health

        # Register all views from the app
        for rule in app.url_map.iter_rules():
            # Skip static and documentation endpoints
            if rule.endpoint.startswith(("static", "docs")):
                continue

            # Get the view function
            view_func = app.view_functions.get(rule.endpoint)
            if view_func and hasattr(view_func, "__doc__") and view_func.__doc__:
                # Check if the docstring contains OpenAPI specification
                if "---" in view_func.__doc__:
                    try:
                        # Register the path with the spec
                        spec.path(view=view_func, app=app)
                    except Exception as e:
                        app.logger.warning(f"Failed to register {rule.endpoint}: {str(e)}")

    return spec
