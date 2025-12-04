from flask import Blueprint, Response, url_for
from pathlib import Path

routes_docs = Blueprint('routes_docs', __name__)

ROOT = Path(__file__).resolve().parents[2]

DOC_MAP = {
    'readme': 'readme.md',
    'configuration': 'CONFIGURATION.md',
    'authentication': 'AUTHENTICATION.md',
    'recent-files': 'RECENT_FILES_FEATURE.md',
    'duplicate-detection': 'DUPLICATE_DETECTION.md'
}

def _render_markdown_basic(md_text: str, title: str, helper_src: str) -> str:
    # Very lightweight markdown-to-HTML: preserve lines, headers, code fences
    # Avoid adding dependencies; this is a simple viewer for offline docs.
    import html
    escaped = html.escape(md_text)
    helper_src = html.escape(helper_src)
    # Convert simple headings and code fences for readability
    escaped = escaped.replace('\n### ', '\n<h4>').replace('\n## ', '\n<h3>').replace('\n# ', '\n<h2>')
    escaped = escaped.replace('```', '</pre>').replace('\n</pre>', '\n</pre>').replace('``', '')
    # Wrap in minimal container
    return f"""
    <!DOCTYPE html>
    <html><head>
    <meta charset="utf-8">
    <title>{html.escape(title)}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{{padding:1rem;}} pre{{background:#f8f9fa;padding:0.75rem;border-radius:6px;}}</style>
    </head><body>
        <div class="container" style="max-width: 900px;">
            <h3 class="mt-2 mb-3">{html.escape(title)}</h3>
            <div class="alert alert-warning d-flex flex-column flex-md-row align-items-md-center gap-2" role="alert">
                <div>
                    <strong>Organizer not running?</strong>
                    <div class="small text-muted">Start it here so referenced data files are recreated automatically.</div>
                </div>
                <div class="ms-md-auto d-flex align-items-center gap-2">
                    <button class="btn btn-outline-secondary btn-sm" id="btn-start-organizer-docs" type="button">Start Organizer</button>
                    <small id="start-organizer-status-docs" class="text-muted"></small>
                </div>
            </div>
      <div class="card"><div class="card-body"><pre>{escaped}</pre></div></div>
    </div>
        <script src="{helper_src}"></script>
        <script>
        document.addEventListener('DOMContentLoaded', function(){{
            if (window.attachStartOrganizerButton) {{
                window.attachStartOrganizerButton('btn-start-organizer-docs', 'start-organizer-status-docs');
            }}
        }});
        </script>
    </body></html>
    """

@routes_docs.route('/docs/<name>')
def view_doc(name: str):
    rel = DOC_MAP.get(name)
    if not rel:
        return Response('Not found', status=404)
    fp = ROOT / rel
    if not fp.exists():
        return Response('Not found', status=404)
    try:
        text = fp.read_text(encoding='utf-8')
        helper_src = url_for('static', filename='js/start_organizer.js')
        html = _render_markdown_basic(text, rel, helper_src)
        return Response(html, mimetype='text/html')
    except Exception as e:
        return Response(f'Error reading doc: {e}', status=500)
