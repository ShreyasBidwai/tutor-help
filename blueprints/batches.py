"""Batch management blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import get_db_connection
from utils import require_login

batches_bp = Blueprint('batches', __name__, url_prefix='')

@batches_bp.route('/batches')
@require_login
def batches():
    """List all batches with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get pagination parameters
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM batches WHERE user_id = ?', (session['user_id'],))
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    # Validate page number
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
    
    # Get paginated batches
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?', 
                   (session['user_id'], per_page, offset))
    batches = cursor.fetchall()
    conn.close()
    return render_template('batches/batches.html', 
                         batches=batches,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page)

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
    
    # Get pagination parameters
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get search query
    search_query = request.args.get('search', '').strip()
    
    # Build base query for counting
    count_query = '''
        SELECT COUNT(*) as total
        FROM students s 
        WHERE s.user_id = ? AND s.batch_id = ?
    '''
    count_params = [session['user_id'], batch_id]
    
    # Build query for fetching data
    query = '''
        SELECT s.*, b.name as batch_name 
        FROM students s 
        LEFT JOIN batches b ON s.batch_id = b.id 
        WHERE s.user_id = ? AND s.batch_id = ?
    '''
    params = [session['user_id'], batch_id]
    
    if search_query:
        query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        count_query += ' AND (s.name LIKE ? OR s.phone LIKE ?)'
        search_pattern = f'%{search_query}%'
        params.extend([search_pattern, search_pattern])
        count_params.extend([search_pattern, search_pattern])
    
    query += ' ORDER BY s.name LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    # Get total count
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    # Validate page number
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
        params[-2] = per_page
        params[-1] = offset
    
    # Get paginated students
    cursor.execute(query, params)
    students = cursor.fetchall()
    
    conn.close()
    return render_template('batches/batch_students.html', 
                         batch=batch,
                         students=students,
                         search_query=search_query,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page)

@batches_bp.route('/batches/add', methods=['GET', 'POST'])
@require_login
def add_batch():
    """Add a new batch"""
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
        
        # Validation
        name = name.strip() if name else ''
        if not name:
            flash('Batch name is required', 'error')
            conn.close()
            return render_template('batches/add_batch.html')
        
        # Validate batch name length (2-100 characters)
        if len(name) < 2:
            flash('Batch name must be at least 2 characters long', 'error')
            conn.close()
            return render_template('batches/add_batch.html')
        
        if len(name) > 100:
            flash('Batch name must be 100 characters or less', 'error')
            conn.close()
            return render_template('batches/add_batch.html')
        
        # Validate time if provided
        if start_time and end_time:
            try:
                from datetime import datetime
                start = datetime.strptime(start_time, '%H:%M').time()
                end = datetime.strptime(end_time, '%H:%M').time()
                if start >= end:
                    flash('End time must be after start time', 'error')
                    conn.close()
                    return render_template('batches/add_batch.html')
            except:
                pass
        
        if name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO batches (name, description, start_time, end_time, days, notifications_enabled, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, start_time, end_time, days, notifications_enabled, session['user_id']))
            conn.commit()
            conn.close()
            flash('Batch created successfully!', 'success')
            conn.close()
            return redirect(url_for('batches.batches'))
    
    conn.close()
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
            # Validation
            name = name.strip() if name else ''
            if not name:
                flash('Batch name is required', 'error')
                conn.close()
                cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
                batch = cursor.fetchone()
                conn.close()
                return render_template('batches/edit_batch.html', batch=batch)
            
            # Validate batch name length (2-100 characters)
            if len(name) < 2:
                flash('Batch name must be at least 2 characters long', 'error')
                conn.close()
                cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
                batch = cursor.fetchone()
                conn.close()
                return render_template('batches/edit_batch.html', batch=batch)
            
            if len(name) > 100:
                flash('Batch name must be 100 characters or less', 'error')
                conn.close()
                cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
                batch = cursor.fetchone()
                conn.close()
                return render_template('batches/edit_batch.html', batch=batch)
            
            # Validate time if provided
            if start_time and end_time:
                try:
                    from datetime import datetime
                    start = datetime.strptime(start_time, '%H:%M').time()
                    end = datetime.strptime(end_time, '%H:%M').time()
                    if start >= end:
                        flash('End time must be after start time', 'error')
                        conn.close()
                        cursor.execute('SELECT * FROM batches WHERE id = ? AND user_id = ?', (batch_id, session['user_id']))
                        batch = cursor.fetchone()
                        conn.close()
                        return render_template('batches/edit_batch.html', batch=batch)
                except:
                    pass
            
            cursor.execute('''
                UPDATE batches 
                SET name = ?, description = ?, start_time = ?, end_time = ?, days = ?, notifications_enabled = ?
                WHERE id = ? AND user_id = ?
            ''', (name, description, start_time, end_time, days, notifications_enabled, batch_id, session['user_id']))
            conn.commit()
            conn.close()
            flash('Batch updated successfully!', 'success')
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

