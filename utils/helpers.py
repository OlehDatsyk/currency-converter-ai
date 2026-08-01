"""
utils/helpers.py
------------------
Small, reusable helper functions that don't belong to a specific
service. Kept separate to avoid cluttering app.py or the services.
"""

from flask import jsonify


def error_response(message, status_code=400):
    """Standard JSON error envelope used across all API routes."""
    return jsonify({"success": False, "error": message}), status_code


def success_response(data, status_code=200):
    """Standard JSON success envelope used across all API routes."""
    return jsonify({"success": True, "data": data}), status_code


def validate_currency_code(code):
    """Basic sanity check — real validation happens against the
    supported-currency list fetched from the API."""
    return isinstance(code, str) and len(code) == 3 and code.isalpha()
