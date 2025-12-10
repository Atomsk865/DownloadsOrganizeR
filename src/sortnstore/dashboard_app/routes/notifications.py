"""Notification Center API endpoints for persistent notification history."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from SortNStoreDashboard.auth.auth import requires_auth

routes_notifications = Blueprint('notifications', __name__)

# Path to notification history file
NOTIFICATIONS_FILE = Path("notification_history.json")


def load_notifications():
    """Load notification history from JSON."""
    try:
        if NOTIFICATIONS_FILE.exists():
            with NOTIFICATIONS_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading notifications: {e}")
        return []


def save_notifications(notifications):
    """Save notification history to JSON."""
    try:
        with NOTIFICATIONS_FILE.open("w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving notifications: {e}")


def cleanup_old_notifications(notifications, days=7):
    """Remove notifications older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    return [n for n in notifications if datetime.fromisoformat(n.get("timestamp", "")) > cutoff]


@routes_notifications.route("/api/notifications", methods=["GET"])
@requires_auth
def get_notifications():
    """Get all notifications, optionally filtered by unread status."""
    notifications = load_notifications()
    
    # Filter by unread if requested
    unread_only = request.args.get("unread", "false").lower() == "true"
    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]
    
    # Get counts
    total = len(load_notifications())
    unread = len([n for n in load_notifications() if not n.get("read", False)])
    
    return jsonify({
        "notifications": notifications[:50],  # Limit to 50 most recent
        "total": total,
        "unread": unread
    })


@routes_notifications.route("/api/notifications", methods=["POST"])
@requires_auth
def add_notification():
    """Add a new notification to history."""
    data = request.get_json()
    
    message = data.get("message", "")
    notification_type = data.get("type", "info")  # info, success, warning, danger
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    notifications = load_notifications()
    
    # Add new notification
    notification = {
        "id": f"notif_{int(datetime.now().timestamp() * 1000)}",
        "message": message,
        "type": notification_type,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    
    notifications.insert(0, notification)
    
    # Cleanup old notifications (older than 7 days)
    notifications = cleanup_old_notifications(notifications)
    
    # Keep only last 100 notifications
    notifications = notifications[:100]
    
    save_notifications(notifications)
    
    return jsonify({"success": True, "notification": notification})


@routes_notifications.route("/api/notifications/<notification_id>/read", methods=["POST"])
@requires_auth
def mark_notification_read(notification_id):
    """Mark a specific notification as read."""
    notifications = load_notifications()
    
    for notif in notifications:
        if notif.get("id") == notification_id:
            notif["read"] = True
            break
    
    save_notifications(notifications)
    
    return jsonify({"success": True})


@routes_notifications.route("/api/notifications/mark-all-read", methods=["POST"])
@requires_auth
def mark_all_read():
    """Mark all notifications as read."""
    notifications = load_notifications()
    
    for notif in notifications:
        notif["read"] = True
    
    save_notifications(notifications)
    
    return jsonify({"success": True})


@routes_notifications.route("/api/notifications/clear", methods=["POST"])
@requires_auth
def clear_notifications():
    """Clear all notifications."""
    save_notifications([])
    return jsonify({"success": True})


@routes_notifications.route("/api/notifications/<notification_id>", methods=["DELETE"])
@requires_auth
def delete_notification(notification_id):
    """Delete a specific notification."""
    notifications = load_notifications()
    
    notifications = [n for n in notifications if n.get("id") != notification_id]
    
    save_notifications(notifications)
    
    return jsonify({"success": True})
