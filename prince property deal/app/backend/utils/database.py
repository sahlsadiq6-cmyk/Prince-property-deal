"""
Database utilities
Handles migrations, queries, and optimizations
"""

from models.models import db, Analytics
from flask import request, current_app
from datetime import datetime


def track_event(event_type, event_data=None, user_id=None):
    """Track user events for analytics"""
    try:
        analytics = Analytics(
            event_type=event_type,
            event_data=event_data,
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if hasattr(request, 'user_agent') else None
        )
        db.session.add(analytics)
        db.session.commit()
    except Exception as e:
        print(f"Error tracking event: {e}")
        db.session.rollback()


def paginate_query(query, page=1, per_page=10):
    """Paginate database query"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def get_analytics_summary(days=30):
    """Get analytics summary for last N days"""
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    analytics = Analytics.query.filter(Analytics.created_at >= cutoff_date).all()
    
    summary = {
        'total_events': len(analytics),
        'events_by_type': {},
        'unique_users': set(),
        'unique_ips': set()
    }
    
    for event in analytics:
        event_type = event.event_type
        if event_type not in summary['events_by_type']:
            summary['events_by_type'][event_type] = 0
        summary['events_by_type'][event_type] += 1
        
        if event.user_id:
            summary['unique_users'].add(event.user_id)
        if event.ip_address:
            summary['unique_ips'].add(event.ip_address)
    
    summary['unique_users'] = len(summary['unique_users'])
    summary['unique_ips'] = len(summary['unique_ips'])
    
    return summary


def bulk_update(model, updates):
    """Bulk update records"""
    try:
        for item_id, data in updates.items():
            item = model.query.get(item_id)
            if item:
                for key, value in data.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
        
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error in bulk update: {e}")
        db.session.rollback()
        return False
