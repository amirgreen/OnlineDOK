from flask import *
from flask.ext.session import Session
import subprocess
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from StorageDevice import StorageDevice
import shutil
from distutils.dir_util import copy_tree
import zipfile
import sys
import datetime
from User import User
from flask_login import current_user, login_user, LoginManager, login_required, logout_user
from DB_Query import DB_Query
from functools import wraps

#ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'])
app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)
sess = Session()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
DBNAME = 'onlineDok.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, DBNAME)
DB = DB_Query(db_path)
context = ('host.cert', 'host.key')


def allowed_file(filename):
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return True


@app.route("/")
@app.route("/index")
def index():
    return render_template("master.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if checkUser(email, password):
            user = User(email)
            login_user(user)
            flash('Logged in successfully.', 'success')
        else:
            flash('Wrong email or password')
            return render_template('login.html')
        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #     return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html')


def checkUser(inputEmail, inputPassword):
    query = 'SELECT * FROM Users WHERE email = "' + inputEmail + '";'
    cursor = DB.executeSelect(query)
    data = [dict(email=row[0], firstName=row[1], lastName=row[2], password=row[3], admin=row[4], suspended=row[5]) for
            row in cursor.fetchall()]
    if data:
        email = data[0]['email']
        password = data[0]['password']
        if check_password_hash(password, inputPassword) and inputEmail == email:
            return True
    return False


# file explorer
@app.route("/drive", methods=['GET'])
@login_required
def drive():
    path = request.args.get('path')
    print path
    print request.form
    from FolderData import FolderData
    if path != '':  # if no path then storage devices
        folder = FolderData(path)
        dirs = folder.dirsInFolder()
        files = folder.filesInFolder()
        app.config['UPLOAD_FOLDER'] = path
        return render_template("drive.html", files=files, dirs=dirs)
    else:
        doks = storages()
        return render_template("storages.html", files=doks)


# On buttons clicked drive
@app.route('/drive', methods=['POST'])
@login_required
def drive_post():
    filePath = ''
    fname = ''
    if request.method == 'POST':
        if request.form['submit'] == 'Upload':
            upload_file()

        if request.form['submit'] == 'Copy':
            copy()

        if request.form['submit'] == 'Paste':
            paste()

        if request.form['submit'] == 'Delete':
            delete()

        if request.form['submit'] == 'Create':
            new_folder()

        if request.form['submit'] == 'Download':
            filePath = download()
            fname = datetime.datetime.now().strftime("download_%d-%m-%Y_%H-%M.zip")

    try:
        return send_file(filePath, as_attachment=True, attachment_filename=fname)
    except Exception as e:
        print e
        return redirect(request.url)
    else:
        os.remove(filePath)


@app.route('/storages')
@login_required
def storages():
    proc = subprocess.Popen("lsblk -i -J -o NAME,TYPE,SIZE,MODEL,MOUNTPOINT,FSTYPE", stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    jsonDoks = json.loads(out)['blockdevices']
    newdoks = []
    partitions = []
    for s in jsonDoks:
        if 'children' in s:
            partitions = s['children']
        dok = StorageDevice(s['name'], s['size'], s['model'], partitions)
        newdoks.append(dok)
        partitions = []
    session['doks'] = newdoks
    session['doksNumber'] = len(jsonDoks)
    print jsonDoks
    return render_template('storages.html', files=newdoks)


@app.route('/update_storages', methods=['POST', 'GET'])
def update_storages():
    proc = subprocess.Popen("lsblk -i -J -o NAME,TYPE,SIZE,MODEL,MOUNTPOINT,FSTYPE", stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    jsonDoks = json.loads(out)['blockdevices']
    answer = 'False'
    if len(jsonDoks) != session['doksNumber']:
        answer = 'True'
        session['doksNumber'] = len(jsonDoks)
    print answer
    return jsonify({'answer': answer})


def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    files = request.files.getlist('file')
    count = 0
    for file in files:
        print file.filename
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print "no file name"
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unicode(filename)))
            count += 1

    print count
    if count == 0:
        return redirect(request.url)
    else:
        flash(str(count) + ' files uploaded', 'success')
        return redirect(url_for('drive',
                                path=app.config['UPLOAD_FOLDER']))


def copy():
    selected_folders = request.form.getlist("folders")
    selected_files = request.form.getlist("files")
    path = app.config['UPLOAD_FOLDER']
    print 'path: ' + path
    count = 0
    for f in selected_folders:
        selected_folders[count] = unicode(path) + '/' + unicode(f)
        count += 1

    count = 0
    for f in selected_files:
        selected_files[count] = unicode(path) + '/' + unicode(f)
        count += 1

    print selected_files
    print selected_folders
    session['files'] = selected_files
    session['folders'] = selected_folders
    flash('Great! now select where you want to copy and press paste', 'info')


def paste():
    folders = session['folders']
    files = session['files']
    for f in files:
        shutil.copy2(unicode(f), unicode(app.config['UPLOAD_FOLDER']))
    for f in folders:
        dir = f.split('/')
        fname = dir[len(dir) - 1]
        dst = unicode(app.config['UPLOAD_FOLDER']) + "/" + unicode(fname)
        # if os.path.isdir(dst):
        #     flash('directory already exist, if you are sure you want to overwrite it, press paste again!',
        #           'alert')
        #     return redirect(url_for('drive', path=app.config['UPLOAD_FOLDER']))
        copy_tree(unicode(f), dst)

    session['files'] = ''
    session['folders'] = ''
    flash('Files copied successfully', 'success')


def delete():
    print 'DELETING'
    selected_folders = request.form.getlist("folders")
    selected_files = request.form.getlist("files")
    path = app.config['UPLOAD_FOLDER']
    for f in selected_files:
        name = unicode(path) + '/' + unicode(f)
        os.remove(name)
    for f in selected_folders:
        name = unicode(path) + '/' + unicode(f)
        shutil.rmtree(name)

    flash('Files deleted successfully', 'success')


def download():
    selected_folders = request.form.getlist("folders")
    selected_files = request.form.getlist("files")
    path = app.config['UPLOAD_FOLDER']
    count = 0
    for f in selected_folders:
        selected_folders[count] = unicode(path) + '/' + unicode(f)
        count += 1

    count = 0
    for f in selected_files:
        selected_files[count] = unicode(path) + '/' + unicode(f)
        count += 1

    output = path + '/file.zip'
    zip_folder(selected_folders, selected_files)
    return output


def new_folder():
    folderName = request.form['folderName']
    newpath = app.config['UPLOAD_FOLDER'] + '/' + folderName
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        flash('Folder created successfully', 'success')
    else:
        flash('There is already a folder named ' + folderName, 'error')


def zip_folder(folders, zfiles):
    """Zip the contents of an entire folder (with that folder included
    in the archive). Empty subfolders will be included in the archive
    as well.
    """
    path = app.config['UPLOAD_FOLDER']
    ziph = zipfile.ZipFile(os.path.join(path, 'file.zip'), 'w', zipfile.ZIP_DEFLATED)
    print folders
    print zfiles
    try:
        for p in folders:
            for root, dirs, files in os.walk(p):
                for file in files:
                    # print 'zipping file: ' + file
                    ziph.write(os.path.join(root, file))
        for f in zfiles:
            print f
            for root, dirs, files in os.walk(os.path.dirname(f)):
                for file in files:
                    if os.path.samefile(f, os.path.join(root, file)):
                        ziph.write(os.path.join(root, file))
        print "'%s' created successfully." % app.config['UPLOAD_FOLDER']
    except IOError, message:
        print message
        sys.exit(1)
    except OSError, message:
        print message
        sys.exit(1)
    except zipfile.BadZipfile, message:
        print message
        sys.exit(1)
    finally:
        ziph.close()


@app.route('/partitions')
def partitions():
    dokIndex = request.args.get('parent')
    doks = session.get('doks')
    print doks
    # session['doks'] = []
    print doks[int(dokIndex)]
    return render_template("partitions.html", partitions=doks[int(dokIndex)].getPartitions())


@app.route('/download_file', methods=['POST'])
def download_file():
    filename = request.args.get('filename')
    return send_file(str(app.config['UPLOAD_FOLDER']) + '/' + str(filename), attachment_filename=filename,
                     as_attachment=True)


@login_manager.user_loader
def load_user(id):
    return User(id)


@app.route('/stream')
def stream():
    path = request.args.get('path')
    return render_template('stream.html', path=path)


@app.route('/change', methods=['GET', 'POST'])
@login_required
def change():
    if request.method == 'POST':
        current = request.form['current']
        new = request.form['new']
        if checkUser(current_user.get_id(), current):
            query = 'UPDATE Users SET password = "' + generate_password_hash(new) + '" WHERE email = "' + current_user.get_id() + '";'
            DB.executeInserUpdateDelete(query)
            flash('password changed successfully.')
        else:
            flash('current password incorrect')
    return render_template('changepass.html')


@app.route("/admin", methods=['GET'])
@login_required
def admin():
    if current_user.admin:
        query = 'SELECT * FROM Users;'
        cursor = DB.executeSelect(query)
        data = [dict(email=row[0], firstName=row[1], lastName=row[2], password=row[3], admin=row[4], suspended=row[5]) for
                row in cursor.fetchall()]
        return render_template("admin.html", users=data)
    else:
        flash("You don't have permission to view this page", 'error')
        return redirect(url_for("index"))


# On buttons clicked drive
@app.route('/admin', methods=['POST'])
def admin_post():
    if request.method == 'POST':
        print request.form['submit']
        if request.form['submit'] == 'Make Admin':
            makeAdmin()

        if request.form['submit'] == 'Delete':
            delete_user()

        if request.form['submit'] == 'Create':
            print 'IM CREATING'
            new_user()

    return redirect(url_for('admin'))


def makeAdmin():
    selected_users = request.form.getlist("users")
    for u in selected_users:
        query = 'UPDATE Users SET admin = 1 WHERE email = "' + u + '";'
        DB.executeInserUpdateDelete(query)
    flash('change successfully.', 'success')


def delete_user():
    selected_users = request.form.getlist("users")
    for u in selected_users:
        if u == current_user.get_id():
            flash('You cannot delete yourself', 'alert')
        elif User(u).admin:
            flash('You cannot delete other admins', 'alert')
        else:
            query = 'DELETE FROM Users WHERE email = "' + u + '";'
            DB.executeInserUpdateDelete(query)
            flash('deleted successfully.', 'success')


def new_user():
    userEmail = request.form['userEmail']
    userFirstName = request.form['userFirstName']
    userLastName = request.form['userLastName']
    if userEmail and userLastName and userFirstName:
        query = 'INSERT INTO Users Values ("{}", "{}", "{}", "{}", {}, {})'.format(userEmail, userFirstName, userLastName, generate_password_hash('1234'), 0, 0)
        try:
            DB.executeInserUpdateDelete(query)
            flash('User created successfully with the default password: 1234', 'success')
        except Exception as e:
            print e
            flash('There is already a user with this email: ' + userEmail, 'error')
    else:
        flash('You must fill all the fields', 'error')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    print str(e)
    print type(e)
    return render_template('500.html', error=str(e)), 500


@app.errorhandler(405)
def page_not_found(e):
    print str(e)
    print type(e)
    return render_template('405.html', error=str(e)), 405


@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))

        return fn(*args, **kwargs)

    return decorated_view


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    print
    return r


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(host='0.0.0.0', port=443, threaded=True, ssl_context=context)
