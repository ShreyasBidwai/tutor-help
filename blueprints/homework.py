"""Homework management blueprint"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from datetime import datetime, date
import os
from database import get_db_connection
from utils import require_login, allowed_file, get_secure_filename
from config import Config

homework_bp = Blueprint('homework', __name__, url_prefix='')

@homework_bp.route('/homework')
@require_login
def homework():
    """List all homework with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get pagination parameters
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as total FROM homework WHERE user_id = ?', (session['user_id'],))
    total_count = cursor.fetchone()['total']
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    # Validate page number
    if page > total_pages and total_pages > 0:
        page = total_pages
        offset = (page - 1) * per_page
    
    # Get paginated homework
    cursor.execute('''
        SELECT h.*, b.name as batch_name, s.name as student_name
        FROM homework h
        LEFT JOIN batches b ON h.batch_id = b.id
        LEFT JOIN students s ON h.student_id = s.id
        WHERE h.user_id = ?
        ORDER BY h.created_at DESC
        LIMIT ? OFFSET ?
    ''', (session['user_id'], per_page, offset))
    homework_list = cursor.fetchall()
    conn.close()
    return render_template('homework/homework.html', 
                         homework_list=homework_list,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page)

@homework_bp.route('/homework/share', methods=['GET', 'POST'])
@require_login
def share_homework():
    """Share homework form"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        batch_id = request.form.get('batch_id') or None
        student_id = request.form.get('student_id') or None
        submission_date = request.form.get('submission_date', '').strip()
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = get_secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('homework', filename)
                full_path = os.path.join(Config.UPLOAD_FOLDER, file_path)
                file.save(full_path)
                file_path = file_path.replace('\\', '/')  # Normalize path
        
        # Validation
        if not title or not title.strip():
            flash('Homework title is required', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
            students = cursor.fetchall()
            conn.close()
            today = date.today().isoformat()
            return render_template('homework/share_homework.html', batches=batches, students=students, today=today)
        
        if not submission_date:
            flash('Submission date is required', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
            students = cursor.fetchall()
            conn.close()
            today = date.today().isoformat()
            return render_template('homework/share_homework.html', batches=batches, students=students, today=today)
        
        # Validate file size
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                if file.content_length and file.content_length > Config.MAX_FILE_SIZE:
                    flash(f'File size exceeds {Config.MAX_FILE_SIZE // (1024*1024)}MB limit', 'error')
                    conn.close()
                    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
                    batches = cursor.fetchall()
                    cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
                    students = cursor.fetchall()
                    conn.close()
                    today = date.today().isoformat()
                    return render_template('homework/share_homework.html', batches=batches, students=students, today=today)
        
        if title:
            if batch_id:
                batch_id = int(batch_id)
            else:
                batch_id = None
            if student_id:
                student_id = int(student_id)
            else:
                student_id = None
            
            # Default to today if no submission date provided
            if not submission_date:
                submission_date = date.today().isoformat()
            
            cursor.execute('''
                INSERT INTO homework (title, content, file_path, youtube_url, batch_id, student_id, submission_date, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, content, file_path, youtube_url, batch_id, student_id, submission_date, session['user_id']))
            conn.commit()
            conn.close()
            flash('Homework shared successfully!', 'success')
            return redirect(url_for('homework.homework'))
    
    # Get batches and students for dropdowns
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
    students = cursor.fetchall()
    
    conn.close()
    
    # Default to today's date
    today = date.today().isoformat()
    
    return render_template('homework/share_homework.html', batches=batches, students=students, today=today)

@homework_bp.route('/uploads/<path:filename>')
@require_login
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import current_app
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@homework_bp.route('/homework/<int:homework_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_homework(homework_id):
    """Edit homework"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        batch_id = request.form.get('batch_id') or None
        student_id = request.form.get('student_id') or None
        submission_date = request.form.get('submission_date', '').strip()
        remove_file = request.form.get('remove_file') == '1'
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = get_secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('homework', filename)
                full_path = os.path.join(Config.UPLOAD_FOLDER, file_path)
                file.save(full_path)
                file_path = file_path.replace('\\', '/')
        
        # Validation
        if not title or not title.strip():
            flash('Homework title is required', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
            students = cursor.fetchall()
            cursor.execute('SELECT * FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
            homework = cursor.fetchone()
            conn.close()
            return render_template('homework/edit_homework.html', homework=homework, batches=batches, students=students, today=date.today().isoformat())
        
        if not submission_date:
            flash('Submission date is required', 'error')
            conn.close()
            cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
            batches = cursor.fetchall()
            cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
            students = cursor.fetchall()
            cursor.execute('SELECT * FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
            homework = cursor.fetchone()
            conn.close()
            return render_template('homework/edit_homework.html', homework=homework, batches=batches, students=students, today=date.today().isoformat())
        
        if title:
            if batch_id:
                batch_id = int(batch_id)
            else:
                batch_id = None
            if student_id:
                student_id = int(student_id)
            else:
                student_id = None
            
            # Default to today if no submission date provided
            if not submission_date:
                submission_date = date.today().isoformat()
            
            # Get existing homework to preserve file_path if not updating
            cursor.execute('SELECT file_path FROM homework WHERE id = ? AND user_id = ?', 
                         (homework_id, session['user_id']))
            existing = cursor.fetchone()
            
            if remove_file:
                file_path = None
            elif not file_path and existing:
                file_path = existing['file_path']
            
            cursor.execute('''
                UPDATE homework 
                SET title = ?, content = ?, file_path = ?, youtube_url = ?, batch_id = ?, student_id = ?, submission_date = ?
                WHERE id = ? AND user_id = ?
            ''', (title, content, file_path, youtube_url, batch_id, student_id, submission_date, homework_id, session['user_id']))
            conn.commit()
            conn.close()
            flash('Homework updated successfully!', 'success')
            return redirect(url_for('homework.homework'))
    
    # Get homework
    cursor.execute('SELECT * FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
    homework = cursor.fetchone()
    
    if not homework:
        conn.close()
        return redirect(url_for('homework.homework'))
    
    # Get batches and students
    cursor.execute('SELECT * FROM batches WHERE user_id = ? ORDER BY name', (session['user_id'],))
    batches = cursor.fetchall()
    
    cursor.execute('SELECT * FROM students WHERE user_id = ? ORDER BY name', (session['user_id'],))
    students = cursor.fetchall()
    
    conn.close()
    
    # Default to today's date if no submission date
    today = date.today().isoformat()
    submission_date = homework['submission_date'] if homework['submission_date'] else today
    
    return render_template('homework/edit_homework.html', homework=homework, batches=batches, students=students, submission_date=submission_date, today=today)

@homework_bp.route('/api/homework/<int:homework_id>', methods=['DELETE'])
@require_login
def delete_homework(homework_id):
    """Delete homework (API endpoint)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM homework WHERE id = ? AND user_id = ?', (homework_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

