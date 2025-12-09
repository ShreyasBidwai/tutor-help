"""Batch management blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_db_connection
from utils import require_login

batches_bp = Blueprint('batches', __name__, url_prefix='')

@batches_bp.route('/batches')
@require_login
def batches():
    """List all batches"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    batches = cursor.fetchall()
    conn.close()
    return render_template('batches/batches.html', batches=batches)

@batches_bp.route('/batches/<int:batch_id>/students')
@require_login
def batch_students(batch_id):
    """View students in a specific batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get batch details
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        flash('Batch not found', 'error')
        return redirect(url_for('batches.batches'))
    
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Build query for students in this batch
    query = '''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ? AND s.batch_id = ?
    '''
    params = [session['user_id'], batch_id]
    
    if search_query:
        query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
    
    query += ' ORDER BY s.name'
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    
    conn.close()
    return render_template('batches/batch_students.html', 
                         batch=batch,
                         students=students,
                         search_query=search_query)

@batches_bp.route('/batches/add', methods=['GET', 'POST'])
@require_login
def add_batch():
    """Add a new batch"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        # Get selected days
        days_list = []
        day_names = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        for day in day_names:
            if request.form.get(f'day_{day}') == 'on':
                days_list.append(day)
        days = ','.join(days_list) if days_list else ''
        
        # Get notifications preference (default to enabled)
        notifications_enabled = 1 if request.form.get('notifications_enabled') == 'on' else 0
        
        if name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO batches (name, description, start_time, end_time, days, notifications_enabled, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, start_time, end_time, days, notifications_enabled, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('batches.batches'))
    
    return render_template('batches/add_batch.html')

@batches_bp.route('/batches/<int:batch_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_batch(batch_id):
    """Edit a batch"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        
        # Get selected days
        days_list = []
        day_names = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        for day in day_names:
            if request.form.get(f'day_{day}') == 'on':
                days_list.append(day)
        days = ','.join(days_list) if days_list else ''
        
        # Get notifications preference (default to enabled)
        notifications_enabled = 1 if request.form.get('notifications_enabled') == 'on' else 0
        
        if name:
            cursor.execute('''
                UPDATE batches 
                SET name = ?, description = ?, start_time = ?, end_time = ?, days = ?, notifications_enabled = ?
                WHERE id = ? AND user_id = ?
            ''', (name, description, start_time, end_time, days, notifications_enabled, batch_id, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('batches.batches'))
    
    # Get batch
    cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    batch = cursor.fetchone()
    
    if not batch:
        conn.close()
        return redirect(url_for('batches.batches'))
    
    # Parse days string to list for template
    batch_days = batch['days'].split(',') if batch['days'] else []
    
    conn.close()
    return render_template('batches/edit_batch.html', batch=batch, batch_days=batch_days)

@batches_bp.route('/api/batches/<int:batch_id>', methods=['DELETE'])
@require_login
def delete_batch(batch_id):
    """Delete a batch (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if batch has students
    cursor.execute('SELECT COUNT(*) as count FROM students WHERE batch_id = ? AND user_id = ?', 
                   (batch_id, session['user_id']))
    student_count = cursor.fetchone()['count']
    
    if student_count > 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Cannot delete batch with students. Please remove students first.'}), 400
    
    cursor.execute('DELETE FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

