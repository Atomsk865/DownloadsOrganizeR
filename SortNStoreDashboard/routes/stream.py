from flask import Blueprint, Response
from SortNStoreDashboard.helpers.helpers import sse_stream
import os

routes_stream = Blueprint('routes_stream', __name__)

@routes_stream.route("/stream/<which>")
def stream(which):
    if which not in ("stdout", "stderr"):
        return "Invalid log type", 400
    import OrganizerDashboard
    STDOUT_LOG = OrganizerDashboard.STDOUT_LOG
    STDERR_LOG = OrganizerDashboard.STDERR_LOG
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    return Response(sse_stream(path), mimetype="text/event-stream")
