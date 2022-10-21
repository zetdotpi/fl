from functools import wraps
from flask import abort
from flask_login import current_user


def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        else:
            abort(403)
    return wrapper


def role_required(role):
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role == role:
                return f(*args, **kwargs)
            else:
                abort(403)
        return wrapper
    return wrap
