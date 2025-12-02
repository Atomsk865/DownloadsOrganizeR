from flask import Blueprint, Response
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

def _render_markdown_basic(md_text: str, title: str) -> str:
    # Very lightweight markdown-to-HTML: preserve lines, headers, code fences
    # Avoid adding dependencies; this is a simple viewer for offline docs.
    import html
    escaped = html.escape(md_text)
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
      <div class="card"><div class="card-body"><pre>{escaped}</pre></div></div>
    </div>
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
        html = _render_markdown_basic(text, rel)
        return Response(html, mimetype='text/html')
    except Exception as e:
        return Response(f'Error reading doc: {e}', status=500)
