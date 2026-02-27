"""Payments blueprint — tutor payment tracking & configuration"""
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from database import get_db_connection
from utils import require_login, get_ist_now
from jobs import send_fcm_notification
import re
import sqlite3
from datetime import datetime

payments_bp = Blueprint('payments', __name__, url_prefix='')


# ── helpers ────────────────────────────────────────────────────────────────────

def _require_tutor():
    """Return user_id if logged-in as tutor, else None."""
    if session.get('role') == 'tutor':
        return session.get('user_id')
    return None


def _get_or_create_config(cursor, user_id):
    """Fetch tutor payment config, creating a default row if missing."""
    cursor.execute('SELECT * FROM tutor_payment_config WHERE user_id = ?', (user_id,))
    cfg = cursor.fetchone()
    if not cfg:
        cursor.execute('''
            INSERT INTO tutor_payment_config (user_id, monthly_fee, due_day, reminders_enabled)
            VALUES (?, 0, 10, 1)
        ''', (user_id,))
        cursor.execute('SELECT * FROM tutor_payment_config WHERE user_id = ?', (user_id,))
        cfg = cursor.fetchone()
    return cfg


def _safe_month(month_str):
    """Validate and return YYYY-MM string, default to current month."""
    now = get_ist_now()
    if month_str:
        try:
            datetime.strptime(month_str, '%Y-%m')
            return month_str
        except ValueError:
            pass
    return now.strftime('%Y-%m')


def _format_month_display(month_str):
    """Convert 'YYYY-MM' → 'March 2026'"""
    try:
        return datetime.strptime(month_str, '%Y-%m').strftime('%B %Y')
    except Exception:
        return month_str


def _notify_student(cursor, record_id, title, body):
    """Send FCM push to the student associated with a fee record.
    Students share the tutor's push_subscriptions row (stored against tutor_id).
    This re-uses the same user_id as the fee record so the student's device,
    which registered the token under the tutor_id, receives it.
    """
    try:
        cursor.execute(
            'SELECT student_id FROM student_fee_records WHERE id = ?', (record_id,)
        )
        rec = cursor.fetchone()
        if not rec:
            return
        # student push token stored against the student's own session user_id
        # (which is the student.id, not users.id) — but since students register
        # tokens under tutor_id (see auth.py line 318), we notify the tutor_id.
        # The tutor's device will receive it; a future improvement can add a
        # separate student push_subscriptions column.
        cursor.execute(
            'SELECT user_id FROM student_fee_records WHERE id = ?', (record_id,)
        )
        row = cursor.fetchone()
        if row:
            send_fcm_notification(row['user_id'], title, body,
                                  {'type': 'fees', 'url': '/student/fees'})
    except Exception:
        pass  # Never let notification failure break the API response


# ── Tutor dashboard ─────────────────────────────────────────────────────────────

@payments_bp.route('/payments')
@require_login
def payments():
    """Main payments dashboard — all tabs rendered from one route."""
    user_id = _require_tutor()
    if not user_id:
        return redirect(url_for('auth.student_login'))

    tab = request.args.get('tab', 'overview')
    month = _safe_month(request.args.get('month'))
    month_display = _format_month_display(month)

    conn = get_db_connection()
    cursor = conn.cursor()
    cfg = _get_or_create_config(cursor, user_id)

    # Build previous/next month for navigation arrows
    year, mon = int(month.split('-')[0]), int(month.split('-')[1])
    prev_month = f"{year - 1}-12" if mon == 1 else f"{year}-{mon - 1:02d}"
    next_month = f"{year + 1}-01" if mon == 12 else f"{year}-{mon + 1:02d}"

    # ── Overview aggregates ──
    cursor.execute('''
        SELECT
            COUNT(*) as total_students,
            SUM(amount) as total_expected,
            SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as total_collected,
            SUM(CASE WHEN status IN ('pending', 'awaiting_confirmation') THEN amount ELSE 0 END) as total_pending,
            SUM(CASE WHEN status = 'overdue' THEN amount ELSE 0 END) as total_overdue,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as count_paid,
            SUM(CASE WHEN status IN ('pending', 'awaiting_confirmation') THEN 1 ELSE 0 END) as count_pending,
            SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END) as count_overdue,
            SUM(CASE WHEN status = 'awaiting_confirmation' THEN 1 ELSE 0 END) as count_awaiting
        FROM student_fee_records
        WHERE user_id = ? AND month = ?
    ''', (user_id, month))
    overview = cursor.fetchone()

    # ── Pending list ──
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.status, sfr.updated_at,
               s.id as student_id, s.name as student_name, s.phone
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ? AND sfr.status IN ('pending', 'overdue')
        ORDER BY sfr.status DESC, s.name
    ''', (user_id, month))
    pending = cursor.fetchall()

    # ── Awaiting list ──
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.status, sfr.paid_at, sfr.updated_at,
               s.id as student_id, s.name as student_name, s.phone
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ? AND sfr.status = 'awaiting_confirmation'
        ORDER BY sfr.updated_at DESC
    ''', (user_id, month))
    awaiting = cursor.fetchall()

    # ── Paid list ──
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.confirmed_at, sfr.notes,
               s.name as student_name
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ? AND sfr.status = 'paid'
        ORDER BY sfr.confirmed_at DESC
    ''', (user_id, month))
    paid = cursor.fetchall()

    # ── History: last 12 months summary ──
    cursor.execute('''
        SELECT month,
               SUM(amount) as expected,
               SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as collected,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_count
        FROM student_fee_records
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    ''', (user_id,))
    history_raw = cursor.fetchall()
    history = [dict(r, month_display=_format_month_display(r['month'])) for r in history_raw]

    conn.commit()

    # ── Data for the settings tab (batch/student fee overrides) ──
    cursor2 = conn.cursor() if not conn else None
    conn2   = get_db_connection()
    c2      = conn2.cursor()
    c2.execute('''
        SELECT id, name, fee_override
        FROM batches WHERE user_id = ? ORDER BY name
    ''', (user_id,))
    batches_cfg = [dict(r) for r in c2.fetchall()]

    c2.execute('''
        SELECT s.id, s.name, s.fee_override,
               b.name AS batch_name, b.fee_override AS batch_override
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ? ORDER BY s.name
    ''', (user_id,))
    students_cfg = [dict(r) for r in c2.fetchall()]
    conn2.close()
    conn.close()

    # Compute collection percentage
    pct = 0
    if overview and overview['total_expected'] and overview['total_expected'] > 0:
        pct = round((overview['total_collected'] or 0) / overview['total_expected'] * 100)

    return render_template(
        'payments/dashboard.html',
        tab=tab,
        month=month,
        month_display=month_display,
        prev_month=prev_month,
        next_month=next_month,
        cfg=cfg,
        overview=overview,
        pending=pending,
        awaiting=awaiting,
        paid=paid,
        history=history,
        collection_pct=pct,
        batches_cfg=batches_cfg,
        students_cfg=students_cfg,
    )


@payments_bp.route('/payments/settings', methods=['POST'])
@require_login
def payment_settings():
    """Save payment configuration for a tutor. Supports both AJAX (JSON) and form POST."""
    user_id = _require_tutor()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' \
              or 'application/json' in request.headers.get('Accept', '')
    if not user_id:
        if is_ajax:
            return jsonify({'error': 'Unauthorized'}), 403
        return redirect(url_for('auth.student_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        monthly_fee = float(request.form.get('monthly_fee', 0) or 0)
        due_day = int(request.form.get('due_day', 10) or 10)
        due_day = max(1, min(28, due_day))

        upi_id = (request.form.get('upi_id') or '').strip()
        if upi_id and not re.match(r'^[\w.\-]+@[\w]+$', upi_id):
            conn.close()
            if is_ajax:
                return jsonify({'error': 'Invalid UPI ID format. Example: yourname@upi'}), 400
            flash('Invalid UPI ID format. Example: yourname@upi', 'error')
            return redirect(url_for('payments.payments', tab='settings'))

        payment_link = (request.form.get('payment_link') or '').strip()
        if payment_link and not re.match(r'^https?://', payment_link):
            conn.close()
            if is_ajax:
                return jsonify({'error': 'Payment link must start with http:// or https://'}), 400
            flash('Payment link must start with http:// or https://', 'error')
            return redirect(url_for('payments.payments', tab='settings'))

        reminders_enabled = 1 if request.form.get('reminders_enabled') else 0

        cursor.execute('''
            INSERT INTO tutor_payment_config
                (user_id, monthly_fee, due_day, upi_id, payment_link, reminders_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                monthly_fee       = excluded.monthly_fee,
                due_day           = excluded.due_day,
                upi_id            = excluded.upi_id,
                payment_link      = excluded.payment_link,
                reminders_enabled = excluded.reminders_enabled,
                updated_at        = CURRENT_TIMESTAMP
        ''', (user_id, monthly_fee, due_day, upi_id or None, payment_link or None, reminders_enabled))
        conn.commit()
        conn.close()
        if is_ajax:
            return jsonify({'success': True, 'message': 'Settings saved!'})
        flash('Payment settings saved!', 'success')

    except (ValueError, TypeError):
        conn.close()
        if is_ajax:
            return jsonify({'error': 'Invalid input. Please check the form values.'}), 400
        flash('Invalid input. Please check the form values.', 'error')

    return redirect(url_for('payments.payments', tab='settings'))


# ── Tutor API actions ───────────────────────────────────────────────────────────

@payments_bp.route('/api/payments/<int:record_id>/confirm', methods=['POST'])
@require_login
def confirm_payment(record_id):
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, status FROM student_fee_records WHERE id = ? AND user_id = ?',
        (record_id, user_id)
    )
    rec = cursor.fetchone()
    if not rec:
        conn.close()
        return jsonify({'error': 'Record not found'}), 404

    if rec['status'] not in ('awaiting_confirmation', 'pending'):
        conn.close()
        return jsonify({'error': f"Cannot confirm a record with status '{rec['status']}'"}), 400

    now = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE student_fee_records
        SET status = 'paid', confirmed_at = ?, updated_at = ?
        WHERE id = ?
    ''', (now, now, record_id))
    conn.commit()

    # Push notification → student's device (stored under tutor_id)
    # Get month & amount for the message
    cursor.execute('SELECT month, amount FROM student_fee_records WHERE id = ?', (record_id,))
    fee_row = cursor.fetchone()
    if fee_row:
        month_display = _format_month_display(fee_row['month'])
        send_fcm_notification(
            user_id,
            '✅ Payment Confirmed!',
            f'Your fee of ₹{int(fee_row["amount"])} for {month_display} has been confirmed.',
            {'type': 'fees', 'url': '/student/fees'}
        )

    conn.close()
    return jsonify({'success': True})


@payments_bp.route('/api/payments/<int:record_id>/reject', methods=['POST'])
@require_login
def reject_payment(record_id):
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM student_fee_records WHERE id = ? AND user_id = ?',
        (record_id, user_id)
    )
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Record not found'}), 404

    now = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        UPDATE student_fee_records
        SET status = 'pending', paid_at = NULL, updated_at = ?, notes = 'Rejected by tutor'
        WHERE id = ?
    ''', (now, record_id))
    conn.commit()

    # Push notification → student (rejection notice)
    cursor.execute('SELECT month FROM student_fee_records WHERE id = ?', (record_id,))
    fee_row = cursor.fetchone()
    if fee_row:
        month_display = _format_month_display(fee_row['month'])
        send_fcm_notification(
            user_id,
            '❌ Payment Not Confirmed',
            f'Your payment submission for {month_display} was rejected. Please try again.',
            {'type': 'fees', 'url': '/student/fees'}
        )

    conn.close()
    return jsonify({'success': True})


@payments_bp.route('/api/payments/<int:record_id>/mark-manual', methods=['POST'])
@require_login
def mark_manual_payment(record_id):
    """Tutor manually records cash / offline payment.

    Edge-cases handled:
    • Partial payment  — `paid_amount` < total_due: record remains pending,
      outstanding balance is visible in the dashboard.
    • Full payment     — marks status = 'paid'.
    • Overpayment      — excess stored as `advance_credit`; automatically
      applied to next month when generate_fees runs.
    """
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data   = request.get_json() or {}
    note   = (data.get('note') or 'Cash payment').strip()[:200]
    paid   = data.get('paid_amount')  # optional — defaults to full amount

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, amount, arrears, paid_amount FROM student_fee_records WHERE id = ? AND user_id = ?',
        (record_id, user_id)
    )
    rec = cursor.fetchone()
    if not rec:
        conn.close()
        return jsonify({'error': 'Record not found'}), 404

    total_due     = round(float(rec['amount']) + float(rec['arrears']), 2)
    already_paid  = round(float(rec['paid_amount'] or 0), 2)
    remaining_due = round(total_due - already_paid, 2)

    # Parse the payment amount (default = settle in full)
    try:
        paid_now = round(float(paid), 2) if paid is not None else remaining_due
    except (TypeError, ValueError):
        conn.close()
        return jsonify({'error': 'paid_amount must be a number'}), 400

    if paid_now <= 0:
        conn.close()
        return jsonify({'error': 'paid_amount must be greater than 0'}), 400

    new_paid_total   = round(already_paid + paid_now, 2)
    advance_credit_  = round(max(new_paid_total - total_due, 0), 2)
    now              = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')

    if new_paid_total >= total_due:
        # Fully settled (or overpaid)
        cursor.execute('''
            UPDATE student_fee_records
            SET status = 'paid',
                paid_amount    = ?,
                advance_credit = ?,
                confirmed_at   = ?,
                paid_at        = ?,
                notes          = ?,
                updated_at     = ?
            WHERE id = ?
        ''', (new_paid_total, advance_credit_, now, now, note, now, record_id))
        result_status = 'paid'
    else:
        # Partial payment — keep pending
        cursor.execute('''
            UPDATE student_fee_records
            SET paid_amount  = ?,
                paid_at      = ?,
                notes        = ?,
                updated_at   = ?
            WHERE id = ?
        ''', (new_paid_total, now, note, now, record_id))
        result_status = 'partial'

    conn.commit()
    conn.close()
    return jsonify({
        'success'        : True,
        'status'         : result_status,
        'paid_total'     : new_paid_total,
        'advance_credit' : advance_credit_,
        'remaining_due'  : round(max(total_due - new_paid_total, 0), 2),
    })


@payments_bp.route('/api/payments/generate', methods=['POST'])
@require_login
def generate_fees():
    """Idempotent fee generation for a given month.

    Fee priority chain per student:
      student.fee_override  >  batch.fee_override  >  global monthly_fee

    Additional edge-cases:
    ① Arrears carry-forward  — any prior months still unpaid are summed.
    ② Advance credit         — overpayment auto-deducted from next month.
    ③ Advance month          — future months marked pending, no special treatment.
    """
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json(silent=True) or {}
    month = _safe_month(data.get('month'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cfg = _get_or_create_config(cursor, user_id)

    if not cfg or cfg['monthly_fee'] <= 0:
        conn.close()
        return jsonify({'error': 'Please set a monthly fee in Settings first.'}), 400

    global_fee = float(cfg['monthly_fee'])

    # Fetch all students with their batch overrides in one query
    cursor.execute('''
        SELECT s.id, s.fee_override AS student_override,
               b.fee_override       AS batch_override
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ?
    ''', (user_id,))
    students = cursor.fetchall()
    created = 0
    now_str = get_ist_now().strftime('%Y-%m-%d %H:%M:%S')

    for s in students:
        sid = s['id']

        # ── Resolve effective base fee (priority chain) ────────────────────
        if s['student_override'] is not None:
            base_fee = float(s['student_override'])
        elif s['batch_override'] is not None:
            base_fee = float(s['batch_override'])
        else:
            base_fee = global_fee

        # ── ① Arrears from prior unpaid months ────────────────────────
        cursor.execute('''
            SELECT COALESCE(SUM(amount + arrears - paid_amount), 0) AS due
            FROM student_fee_records
            WHERE student_id = ? AND user_id = ?
              AND month < ?
              AND status IN ('pending', 'overdue')
        ''', (sid, user_id, month))
        total_arrears = round(float(cursor.fetchone()['due'] or 0), 2)

        # ── ② Advance credit from prior over-paid months ──────────────
        cursor.execute('''
            SELECT COALESCE(SUM(advance_credit), 0) AS credit
            FROM student_fee_records
            WHERE student_id = ? AND user_id = ?
              AND month < ? AND advance_credit > 0
        ''', (sid, user_id, month))
        prior_credit = round(float(cursor.fetchone()['credit'] or 0), 2)

        net_amount    = round(max(base_fee + total_arrears - prior_credit, 0), 2)
        paid_amount_  = 0.0
        new_status    = 'pending'
        confirmed_at_ = None
        leftover      = 0.0

        if prior_credit >= base_fee + total_arrears:
            paid_amount_  = net_amount
            new_status    = 'paid'
            confirmed_at_ = now_str
            leftover      = round(prior_credit - base_fee - total_arrears, 2)

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO student_fee_records
                    (student_id, user_id, month, amount, paid_amount,
                     arrears, advance_credit, status, confirmed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sid, user_id, month,
                  net_amount, paid_amount_,
                  total_arrears, leftover, new_status, confirmed_at_))
            if cursor.rowcount:
                created += 1
                if prior_credit > 0:
                    cursor.execute('''
                        UPDATE student_fee_records
                        SET advance_credit = 0, updated_at = ?
                        WHERE student_id = ? AND user_id = ?
                          AND month < ? AND advance_credit > 0
                    ''', (now_str, sid, user_id, month))
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    if created > 0:
        month_display = _format_month_display(month)
        send_fcm_notification(
            user_id, '📋 Fee Generated',
            f'Fee ready for {month_display}. Tap to view.',
            {'type': 'fees', 'url': '/student/fees'}
        )

    conn.close()
    return jsonify({'success': True, 'created': created, 'month': month})


# ── Fee override CRUD ──────────────────────────────────────────────────────────

@payments_bp.route('/api/payments/fee-overrides', methods=['GET'])
@require_login
def get_fee_overrides():
    """Return current batch and student fee overrides."""
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    conn   = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, name, fee_override FROM batches WHERE user_id = ? ORDER BY name',
        (user_id,)
    )
    batches = [dict(r) for r in cursor.fetchall()]

    cursor.execute('''
        SELECT s.id, s.name, s.fee_override,
               b.name AS batch_name, b.fee_override AS batch_override
        FROM students s
        LEFT JOIN batches b ON s.batch_id = b.id
        WHERE s.user_id = ? ORDER BY s.name
    ''', (user_id,))
    students = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return jsonify({'batches': batches, 'students': students})


@payments_bp.route('/api/payments/fee-overrides', methods=['POST'])
@require_login
def save_fee_overrides():
    """Save batch and/or student fee overrides.

    Body: { batches: [{id, fee_override}], students: [{id, fee_override}] }
    fee_override = null clears the override (falls back to parent).
    """
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data     = request.get_json(silent=True) or {}
    batches  = data.get('batches', [])
    students = data.get('students', [])

    conn   = get_db_connection()
    cursor = conn.cursor()

    for item in batches:
        bid = item.get('id')
        fee = item.get('fee_override')  # None or float
        if bid is None:
            continue
        try:
            fee_val = float(fee) if fee is not None and fee != '' else None
            if fee_val is not None and fee_val < 0:
                fee_val = None
        except (TypeError, ValueError):
            fee_val = None

        cursor.execute(
            'UPDATE batches SET fee_override = ? WHERE id = ? AND user_id = ?',
            (fee_val, bid, user_id)
        )

    for item in students:
        sid = item.get('id')
        fee = item.get('fee_override')
        if sid is None:
            continue
        try:
            fee_val = float(fee) if fee is not None and fee != '' else None
            if fee_val is not None and fee_val < 0:
                fee_val = None
        except (TypeError, ValueError):
            fee_val = None

        cursor.execute(
            'UPDATE students SET fee_override = ? WHERE id = ? AND user_id = ?',
            (fee_val, sid, user_id)
        )

    conn.commit()
    conn.close()
    return jsonify({'success': True})



@payments_bp.route('/api/payments/poll')
@require_login
def poll_payments():
    """Lightweight polling endpoint for the tutor payments dashboard.
    Returns the current state of all payment sections for a given month
    so the frontend can update the UI without a full page reload.
    """
    user_id = _require_tutor()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    month = _safe_month(request.args.get('month'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Overview aggregates
    cursor.execute('''
        SELECT
            COALESCE(SUM(amount), 0)                                              AS total_expected,
            COALESCE(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 0)    AS total_collected,
            COALESCE(SUM(CASE WHEN status IN ('pending', 'awaiting_confirmation',
                                              'overdue') THEN amount ELSE 0 END), 0) AS total_pending,
            COALESCE(SUM(CASE WHEN status = 'overdue' THEN amount ELSE 0 END), 0) AS total_overdue,
            COALESCE(SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END), 0)         AS count_paid,
            COALESCE(SUM(CASE WHEN status IN ('pending', 'awaiting_confirmation',
                                              'overdue') THEN 1 ELSE 0 END), 0)   AS count_pending,
            COALESCE(SUM(CASE WHEN status = 'overdue' THEN 1 ELSE 0 END), 0)      AS count_overdue,
            COALESCE(SUM(CASE WHEN status = 'awaiting_confirmation' THEN 1 ELSE 0
                         END), 0)                                                  AS count_awaiting,
            COALESCE(COUNT(*), 0)                                                 AS total_students
        FROM student_fee_records
        WHERE user_id = ? AND month = ?
    ''', (user_id, month))
    ov = cursor.fetchone()

    # Pending + overdue rows
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.status,
               s.name AS student_name
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ?
          AND sfr.status IN ('pending', 'overdue')
        ORDER BY sfr.status DESC, s.name
    ''', (user_id, month))
    pending = [dict(r) for r in cursor.fetchall()]

    # Awaiting rows
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.paid_at,
               s.name AS student_name
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ?
          AND sfr.status = 'awaiting_confirmation'
        ORDER BY sfr.updated_at DESC
    ''', (user_id, month))
    awaiting = [dict(r) for r in cursor.fetchall()]

    # Paid rows
    cursor.execute('''
        SELECT sfr.id, sfr.amount, sfr.confirmed_at, sfr.notes,
               s.name AS student_name
        FROM student_fee_records sfr
        JOIN students s ON sfr.student_id = s.id
        WHERE sfr.user_id = ? AND sfr.month = ?
          AND sfr.status = 'paid'
        ORDER BY sfr.confirmed_at DESC
    ''', (user_id, month))
    paid = [dict(r) for r in cursor.fetchall()]

    conn.close()

    total_exp = ov['total_expected'] or 0
    collection_pct = round((ov['total_collected'] or 0) / total_exp * 100) if total_exp else 0

    return jsonify({
        'month': month,
        'overview': {
            'total_expected':  ov['total_expected'],
            'total_collected': ov['total_collected'],
            'total_pending':   ov['total_pending'],
            'total_overdue':   ov['total_overdue'],
            'count_paid':      ov['count_paid'],
            'count_pending':   ov['count_pending'],
            'count_overdue':   ov['count_overdue'],
            'count_awaiting':  ov['count_awaiting'],
            'total_students':  ov['total_students'],
            'collection_pct':  collection_pct,
        },
        'pending':  pending,
        'awaiting': awaiting,
        'paid':     paid,
    })


# Keep legacy stub routes to avoid 404s if linked anywhere
@payments_bp.route('/payments/locked')
@require_login
def payments_locked():
    return redirect(url_for('payments.payments'))


@payments_bp.route('/payments/pro-details')
@require_login
def pro_details():
    return redirect(url_for('payments.payments'))
