from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, send_file
import os, io, zipfile
from datetime import datetime
from auth import login_user, logout_user, is_logged_in, is_admin, refresh_session_role, get_all_users, update_user
from database import init_db
import shutil

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

def format_size(n):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f"{round(n, 2)} {unit}"
        n /= 1024
    return f"{round(n, 2)} TB"

def get_file_info(path):
    files = []
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        if os.path.isfile(fp):
            files.append({
                'name': f,
                'date': datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M'),
                'size': format_size(os.path.getsize(fp))
            })
    return sorted(files, key=lambda x: x['date'], reverse=True)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if login_user(request.form['username'], request.form['password']):
            return redirect(url_for('upload'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_logged_in():
        return redirect(url_for('login'))

    if is_admin():
        return redirect(url_for('admin'))

    user = session['user']['username']
    folder = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(folder, exist_ok=True)

    if request.method == 'POST':
        for f in request.files.getlist('files'):
            if f.filename:
                f.save(os.path.join(folder, f.filename))

    files = get_file_info(folder)
    return render_template('upload.html', files=files, username=user)

@app.route('/uploads/<user>/<filename>')
def download_file(user, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, user), filename)

@app.route('/<user>/delete_multiple', methods=['POST'])
def delete_multiple(user):
    if not is_logged_in() or (session['user']['username'] != user and not is_admin()):
        return "Unauthorized", 403

    for fname in request.form.getlist('files_to_delete'):
        fp = os.path.join(UPLOAD_FOLDER, user, fname)
        if os.path.exists(fp):
            os.remove(fp)
    return redirect(url_for('upload'))

@app.route('/download_multiple/<user>', methods=['POST'])
def download_multiple(user):
    if not is_logged_in() or (session['user']['username'] != user and not is_admin()):
        return "Unauthorized", 403

    z = io.BytesIO()
    with zipfile.ZipFile(z, 'w') as zipf:
        for fname in request.form.getlist('files_to_download'):
            fp = os.path.join(UPLOAD_FOLDER, user, fname)
            if os.path.exists(fp):
                zipf.write(fp, arcname=fname)
    z.seek(0)
    return send_file(z, as_attachment=True, download_name=f"{user}_files.zip")

@app.route('/admin', methods=['GET'])
def admin():
    if not is_logged_in() or not is_admin():
        return redirect(url_for('login'))

    from auth import get_all_users
    all_users = [u[1] for u in get_all_users()]  # use username (str)
    data = {}

    for u in all_users:
        path = os.path.join(UPLOAD_FOLDER, u)
        files = get_file_info(path) if os.path.isdir(path) else []
        data[u] = files

    current_admin = session['user']['username']
    return render_template('admin.html', data=data, current_user=current_admin)



@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    if not is_logged_in() or not is_admin():
        return redirect(url_for('login'))

    target_user = request.form.get('target_user')
    if not target_user:
        return "No user selected", 400

    folder = os.path.join(UPLOAD_FOLDER, target_user)
    os.makedirs(folder, exist_ok=True)

    for f in request.files.getlist('files'):
        if f.filename:
            f.save(os.path.join(folder, f.filename))

    return redirect(url_for('admin'))

@app.route('/admin/delete_multiple', methods=['POST'])
def admin_delete_multiple():
    if not is_logged_in() or not is_admin():
        return "Unauthorized", 403

    for entry in request.form.getlist('files_to_delete'):
        if '|||' in entry:
            u, f = entry.split('|||', 1)
            fp = os.path.join(UPLOAD_FOLDER, u, f)
            if os.path.exists(fp):
                os.remove(fp)
    return redirect(url_for('admin'))

@app.route('/delete_all/<user>', methods=['POST'])
def delete_all(user):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user)
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
        os.makedirs(user_folder)  # recreate the folder
    return redirect(url_for('upload'))

@app.route('/admin/delete_all', methods=['POST'])
def admin_delete_all():
    if not is_logged_in() or not is_admin():
        return "Unauthorized", 403

    username = request.form.get('username')
    if not username:
        return "Missing username", 400

    folder = os.path.join(UPLOAD_FOLDER, username)
    if os.path.exists(folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    return redirect(url_for('admin'))



@app.route('/admin_download_multiple', methods=['POST'])
def admin_download_multiple():
    if not is_logged_in() or not is_admin():
        return "Unauthorized", 403

    z = io.BytesIO()
    with zipfile.ZipFile(z, 'w') as zipf:
        for entry in request.form.getlist('files_to_download'):
            u, f = entry.split('|||')
            fp = os.path.join(UPLOAD_FOLDER, u, f)
            if os.path.exists(fp):
                zipf.write(fp, arcname=f"{u}/{f}")
    z.seek(0)
    return send_file(z, as_attachment=True, download_name="admin_selected.zip")

@app.route('/create_user', methods=['GET', 'POST'])
def create_user_page():
    from auth import create_user
    if not is_logged_in() or not is_admin():
        return redirect(url_for('login'))

    msg = err = None
    if request.method == 'POST':
        if create_user(request.form['username'], request.form['password'], request.form['role']):
            msg = "✅ User created."
        else:
            err = "❌ Username exists."
    return render_template('create_user.html', message=msg, error=err)

@app.route('/edit_users', methods=['GET', 'POST'])
def edit_users():
    from auth import get_user
    refresh_session_role()
    if not is_logged_in() or not is_admin():
        return redirect(url_for('login'))

    users = get_all_users()
    msg = err = None

    if request.method == 'POST':
        uid = int(request.form['id'])
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        r = request.form['role']
        cur = next((x for x in users if x[0] == uid), None)

        if not cur:
            err = "User not found."
        elif sum(1 for x in users if x[2] == 'admin') == 1 and cur[2] == 'admin' and r != 'admin':
            err = "❌ Cannot remove last admin"
        else:
            update_user(uid, u, p, r)  # Let the function handle password logic
            msg = "✅ Updated"
            users = get_all_users()


    return render_template('edit_users.html', users=users, message=msg, error=err)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback to 5000 for local
    app.run(host="0.0.0.0", port=port, debug=True)
