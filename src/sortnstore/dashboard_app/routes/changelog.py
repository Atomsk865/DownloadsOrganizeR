"""Route to serve changelog file."""

from pathlib import Path
from flask import Blueprint, send_file

routes_changelog = Blueprint('changelog', __name__)

CHANGELOG_PATH = Path(__file__).parent.parent.parent / "CHANGELOG.md"


@routes_changelog.route("/CHANGELOG.md", methods=["GET"])
def get_changelog():
    """Serve the changelog markdown file."""
    if CHANGELOG_PATH.exists():
        return send_file(CHANGELOG_PATH, mimetype='text/markdown')
    return "Changelog not found", 404
