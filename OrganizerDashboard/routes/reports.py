from flask import Blueprint, jsonify, request
import smtplib
from email.message import EmailMessage
import json
import os
from pathlib import Path
from base64 import b64decode

reports_bp = Blueprint('reports', __name__)

CONFIG_PATH = Path('C:/Scripts/organizer_config.json')
FILE_MOVES_JSON = Path('C:/Scripts/file_moves.json')


def load_json(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def send_email(smtp_cfg: dict, subject: str, body: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_cfg.get('from')
    msg['To'] = smtp_cfg.get('to')
    msg.set_content(body)

    host = smtp_cfg.get('host')
    port = int(smtp_cfg.get('port', 587))
    user = smtp_cfg.get('username')
    pw = smtp_cfg.get('password')
    use_tls = bool(smtp_cfg.get('tls', True))

    with smtplib.SMTP(host, port) as s:
        if use_tls:
            s.starttls()
        if user and pw:
            s.login(user, pw)
        s.send_message(msg)


@reports_bp.route('/api/reports/weekly', methods=['POST'])
def trigger_weekly_report():
    cfg = load_json(CONFIG_PATH)
    smtp = cfg.get('smtp') or {}
    if not smtp.get('host') or not smtp.get('to') or not smtp.get('from'):
        return jsonify({'error': 'SMTP not configured'}), 400

    moves = load_json(FILE_MOVES_JSON)
    lines = []
    if isinstance(moves, list):
        for m in moves[:50]:
            lines.append(f"{m.get('timestamp','')} - {m.get('filename','')} => {m.get('destination_path','')}")
    body = "Weekly DownloadsOrganizeR summary (latest moves):\n\n" + "\n".join(lines)

    try:
        send_email(smtp, 'DownloadsOrganizeR Weekly Summary', body)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/api/test/smtp', methods=['POST'])
def test_smtp():
    """Test SMTP settings by sending a test email."""
    data = request.get_json() or {}
    host = data.get('host')
    port = int(data.get('port', 587))
    from_addr = data.get('from')
    to_addr = data.get('to')
    user = data.get('username')
    pw = data.get('password')
    use_tls = bool(data.get('tls', True))

    if not host or not from_addr or not to_addr:
        return jsonify({'error': 'Host, from, and to addresses required'}), 400

    try:
        msg = EmailMessage()
        msg['Subject'] = 'DownloadsOrganizeR SMTP Test'
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg.set_content('This is a test email from DownloadsOrganizeR dashboard. SMTP configuration is working correctly.')

        with smtplib.SMTP(host, port, timeout=10) as s:
            if use_tls:
                s.starttls()
            if user and pw:
                s.login(user, pw)
            s.send_message(msg)
        return jsonify({'success': True, 'message': f'Test email sent to {to_addr}'})
    except Exception as e:
        return jsonify({'error': f'SMTP test failed: {str(e)}'}), 500


@reports_bp.route('/api/test/nas', methods=['POST'])
def test_nas():
    """Test network target UNC path reachability and write access."""
    data = request.get_json() or {}
    path = data.get('path')
    cred_key = data.get('credential_key')

    if not path:
        return jsonify({'error': 'UNC path required'}), 400

    # Load credentials if key provided
    cfg = {}
    try:
        with CONFIG_PATH.open('r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception:
        pass

    creds = cfg.get('credentials', {}).get(cred_key) if cred_key else None
    username = creds.get('username') if creds else None
    password_b64 = creds.get('password_b64') if creds else None
    password = None
    if password_b64:
        try:
            password = b64decode(password_b64).decode('utf-8')
        except Exception:
            pass

    # Attempt to access the path
    # Note: On Windows, net use or mounting may be required for SMB with credentials
    # Here we do a simple existence and write test
    try:
        p = Path(path)
        # Check if path exists or can be created
        if not p.exists():
            return jsonify({'error': f'Path not accessible or does not exist: {path}'}), 400
        # Attempt write test
        test_file = p / '.organizer_test'
        test_file.write_text('test')
        test_file.unlink()
        return jsonify({'success': True, 'message': f'NAS path {path} is accessible and writable'})
    except PermissionError:
        return jsonify({'error': f'Permission denied for {path}. Check credentials.'}), 403
    except Exception as e:
        return jsonify({'error': f'NAS test failed: {str(e)}'}), 500
