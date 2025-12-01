from flask import Blueprint, jsonify

routes_service_name = Blueprint('routes_service_name', __name__)

SERVICE_NAME = "DownloadsOrganizer"

@routes_service_name.route('/service_name')
def service_name():
    """Return the configured Windows service name used by the dashboard/installer."""
    return jsonify({"service_name": SERVICE_NAME})
