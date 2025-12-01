from flask import Blueprint, Response
from OrganizerDashboard.helpers.helpers import sse_stream
import os

routes_stream = Blueprint('routes_stream', __name__)

@routes_stream.route("/stream/<which>")
def stream(which):
    if which not in ("stdout", "stderr"):
        return "Invalid log type", 400
    from OrganizerDashboard.OrganizerDashboard import STDOUT_LOG, STDERR_LOG
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    return Response(sse_stream(path), mimetype="text/event-stream")
