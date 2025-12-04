"""Statistics API endpoints for file organization analytics."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from flask import Blueprint, jsonify, render_template
from OrganizerDashboard.auth.auth import requires_auth
import os

routes_statistics = Blueprint('statistics', __name__)

# Path to file moves log
ROOT = Path(__file__).resolve().parents[2]
FILE_MOVES_JSON = ROOT / "config" / "json" / "file_moves.json"


def load_file_moves():
    """Load file move history from JSON."""
    try:
        # Feature gating via organizer_config.json
        cfg_path = ROOT / 'organizer_config.json'
        try:
            if cfg_path.exists():
                with cfg_path.open('r', encoding='utf-8') as f:
                    cfg = json.load(f)
                feats = cfg.get('features') or {}
                if feats.get('reports_enabled') is False:
                    return []
        except Exception:
            pass
        if FILE_MOVES_JSON.exists():
            with FILE_MOVES_JSON.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading file moves: {e}")
        return []


def parse_timestamp(ts_str):
    """Parse ISO format timestamp."""
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


@routes_statistics.route("/api/statistics/overview", methods=["GET"])
@requires_auth
def get_statistics_overview():
    """Get overview statistics for the dashboard."""
    moves = load_file_moves()
    
    if not moves:
        return jsonify({
            "total_files": 0,
            "total_categories": 0,
            "today_count": 0,
            "week_count": 0,
            "month_count": 0,
            "total_size_mb": 0,
            "avg_per_day": 0
        })
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    today_count = 0
    week_count = 0
    month_count = 0
    categories = set()
    oldest_date = now
    
    for move in moves:
        ts = parse_timestamp(move.get("timestamp", ""))
        if ts:
            if ts >= today_start:
                today_count += 1
            if ts >= week_start:
                week_count += 1
            if ts >= month_start:
                month_count += 1
            if ts < oldest_date:
                oldest_date = ts
        
        category = move.get("category", "Other")
        categories.add(category)
    
    # Calculate average per day
    days_active = max((now - oldest_date).days, 1)
    avg_per_day = round(len(moves) / days_active, 1)
    
    return jsonify({
        "total_files": len(moves),
        "total_categories": len(categories),
        "today_count": today_count,
        "week_count": week_count,
        "month_count": month_count,
        "avg_per_day": avg_per_day,
        "oldest_date": oldest_date.isoformat() if oldest_date != now else now.isoformat()
    })


@routes_statistics.route("/api/statistics/by-category", methods=["GET"])
@requires_auth
def get_statistics_by_category():
    """Get file count breakdown by category."""
    moves = load_file_moves()
    
    category_counts = Counter()
    for move in moves:
        category = move.get("category", "Other")
        category_counts[category] += 1
    
    # Format for Chart.js
    categories = []
    counts = []
    for cat, count in category_counts.most_common():
        categories.append(cat)
        counts.append(count)
    
    return jsonify({
        "labels": categories,
        "data": counts
    })


@routes_statistics.route("/api/statistics/by-extension", methods=["GET"])
@requires_auth
def get_statistics_by_extension():
    """Get top file extensions organized."""
    moves = load_file_moves()
    
    ext_counts = Counter()
    for move in moves:
        filename = move.get("filename", "")
        if "." in filename:
            ext = filename.rsplit(".", 1)[-1].lower()
            ext_counts[ext] += 1
    
    # Get top 10
    top_extensions = []
    top_counts = []
    for ext, count in ext_counts.most_common(10):
        top_extensions.append(f".{ext}")
        top_counts.append(count)
    
    return jsonify({
        "labels": top_extensions,
        "data": top_counts
    })


@routes_statistics.route("/api/statistics/timeline", methods=["GET"])
@requires_auth
def get_statistics_timeline():
    """Get daily activity timeline for the last 30 days."""
    moves = load_file_moves()
    
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Initialize daily counts
    daily_counts = defaultdict(int)
    
    for move in moves:
        ts = parse_timestamp(move.get("timestamp", ""))
        if ts and ts >= thirty_days_ago:
            date_key = ts.strftime("%Y-%m-%d")
            daily_counts[date_key] += 1
    
    # Create sorted list of last 30 days
    dates = []
    counts = []
    current_date = thirty_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(31):
        date_key = current_date.strftime("%Y-%m-%d")
        dates.append(date_key)
        counts.append(daily_counts.get(date_key, 0))
        current_date += timedelta(days=1)
    
    return jsonify({
        "labels": dates,
        "data": counts
    })


@routes_statistics.route("/api/statistics/recent-files", methods=["GET"])
@requires_auth
def get_recent_files():
    """Get the 20 most recently organized files."""
    moves = load_file_moves()
    
    recent = []
    for move in moves[:20]:  # Already sorted most recent first
        ts = parse_timestamp(move.get("timestamp", ""))
        recent.append({
            "filename": move.get("filename", "Unknown"),
            "category": move.get("category", "Other"),
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S") if ts else "Unknown",
            "destination": move.get("destination_path", "")
        })
    
    return jsonify({"files": recent})


@routes_statistics.route("/api/statistics/hourly-activity", methods=["GET"])
@requires_auth
def get_hourly_activity():
    """Get activity heatmap by hour of day."""
    moves = load_file_moves()
    
    hourly_counts = [0] * 24
    
    for move in moves:
        ts = parse_timestamp(move.get("timestamp", ""))
        if ts:
            hourly_counts[ts.hour] += 1
    
    labels = [f"{h:02d}:00" for h in range(24)]
    
    return jsonify({
        "labels": labels,
        "data": hourly_counts
    })


@routes_statistics.route("/statistics/full", methods=["GET"])
@requires_auth
def statistics_full_view():
    """Render a standalone full-view statistics page with charts."""
    return render_template('statistics_full.html')
