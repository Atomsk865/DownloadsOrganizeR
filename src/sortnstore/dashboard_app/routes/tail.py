from flask import Blueprint, request
from SortNStoreDashboard.helpers.helpers import last_n_lines_normalized
import os

routes_tail = Blueprint('routes_tail', __name__)

@routes_tail.route("/tail/<which>")
def tail(which):
    if which not in ("stdout", "stderr"):
        return "Invalid log type", 400
    import SortNStoreDashboard
    STDOUT_LOG = SortNStoreDashboard.STDOUT_LOG
    STDERR_LOG = SortNStoreDashboard.STDERR_LOG
    path = STDOUT_LOG if which == "stdout" else STDERR_LOG
    lines = int(request.args.get("lines", "200"))
    return last_n_lines_normalized(path, lines)
