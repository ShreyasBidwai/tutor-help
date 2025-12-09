"""Payments management blueprint"""
from flask import Blueprint, render_template
from utils import require_login

payments_bp = Blueprint('payments', __name__, url_prefix='')

@payments_bp.route('/payments/locked')
@require_login
def payments_locked():
    """Locked payment management system"""
    return render_template('payments/payments_locked.html')

