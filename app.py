import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import random

# Thiết lập ứng dụng Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max-limit

# Đảm bảo thư mục uploads tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Khởi tạo cơ sở dữ liệu
db = SQLAlchemy(app)

# Định nghĩa các mô hình dữ liệu
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200), default='default.png')
    is_admin = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in-progress, completed
    created = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Hàm tạo cơ sở dữ liệu và dữ liệu mẫu
@app.cli.command('init-db')
def init_db():
    db.drop_all()
    db.create_all()
    
    # Tạo admin
    admin = User(
        email='pvnhuong2405@gmail.com',
        password=generate_password_hash('admin123'),
        name='Administrator',
        is_admin=True,
        avatar='default.png'
    )
    
    # Tạo các danh mục mẫu
    categories = [
        Category(name='Công việc'),
        Category(name='Học tập'),
        Category(name='Cá nhân'),
        Category(name='Khác')
    ]
    
    db.session.add(admin)
    for category in categories:
        db.session.add(category)
    
    db.session.commit()
    print('Đã khởi tạo cơ sở dữ liệu và dữ liệu mẫu.')

# Hàm kiểm tra người dùng đã đăng nhập
def is_logged_in():
    return 'user_id' in session

# Hàm kiểm tra người dùng là admin
def is_admin():
    if not is_logged_in():
        return False
    user = User.query.get(session['user_id'])
    return user and user.is_admin

# Hàm tạo avatar ngẫu nhiên
def get_random_avatar():
    # Dùng Liara avatar placeholder service hoặc tạo ngẫu nhiên
    gender = random.choice(['male', 'female'])
    index = random.randint(1, 100)
    return f"https://avatar-placeholder.iran.liara.run/public/{gender}/{index}"

# Routes
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    
    # Lấy tất cả tasks của người dùng
    if user.is_admin:
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(user_id=user.id).all()
    
    # Đếm số công việc quá hạn
    overdue_tasks = []
    for task in tasks:
        if task.due_date and task.status != 'completed' and task.due_date < datetime.utcnow():
            overdue_tasks.append(task)
    
    return render_template('index.html', user=user, tasks=tasks, categories=categories, overdue_count=len(overdue_tasks))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Email hoặc mật khẩu không đúng')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Kiểm tra email đã tồn tại
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email đã được sử dụng')
            return redirect(url_for('register'))
        
        # Set admin nếu email trùng với email admin
        is_admin = (email == 'pvnhuong2405@gmail.com')
        
        # Tạo avatar ngẫu nhiên
        avatar = get_random_avatar()
        
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            name=name,
            avatar=avatar,
            is_admin=is_admin
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Xử lý upload avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.avatar = filename
        
        # Xử lý thay đổi avatar ngẫu nhiên
        if 'random_avatar' in request.form:
            user.avatar = get_random_avatar()
        
        user.name = name
        db.session.commit()
        flash('Cập nhật thông tin thành công!')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/tasks/add', methods=['GET', 'POST'])
def add_task():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        due_date_str = request.form.get('due_date')
        
        # Chuyển đổi chuỗi ngày thành đối tượng datetime
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Định dạng ngày không hợp lệ')
                return redirect(url_for('add_task'))
        
        new_task = Task(
            title=title,
            description=description,
            user_id=user.id,
            category_id=category_id,
            due_date=due_date
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        flash('Đã thêm công việc mới!')
        return redirect(url_for('index'))
    
    return render_template('task_form.html', user=user, categories=categories)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    task = Task.query.get_or_404(task_id)
    categories = Category.query.all()
    
    # Kiểm tra quyền chỉnh sửa
    if task.user_id != user.id and not user.is_admin:
        flash('Bạn không có quyền chỉnh sửa công việc này')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.category_id = request.form.get('category_id')
        task.status = request.form.get('status')
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Định dạng ngày không hợp lệ')
                return redirect(url_for('edit_task', task_id=task_id))
        
        # Cập nhật thời gian hoàn thành nếu trạng thái là "completed"
        if task.status == 'completed' and not task.finished:
            task.finished = datetime.utcnow()
        elif task.status != 'completed':
            task.finished = None
        
        db.session.commit()
        flash('Đã cập nhật công việc!')
        return redirect(url_for('index'))
    
    # Format due_date for HTML datetime-local input
    due_date_str = ''
    if task.due_date:
        due_date_str = task.due_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('task_form.html', user=user, task=task, categories=categories, due_date_str=due_date_str)

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    task = Task.query.get_or_404(task_id)
    
    # Kiểm tra quyền xóa
    if task.user_id != user.id and not user.is_admin:
        flash('Bạn không có quyền xóa công việc này')
        return redirect(url_for('index'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Đã xóa công việc!')
    return redirect(url_for('index'))

# Quản lý danh mục (chỉ admin)
@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if not is_logged_in() or not is_admin():
        flash('Bạn không có quyền truy cập trang này')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    categories = Category.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        if name:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            flash('Đã thêm danh mục mới!')
        else:
            flash('Tên danh mục không được để trống')
    
    return render_template('categories.html', user=user, categories=categories)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    if not is_logged_in() or not is_admin():
        flash('Bạn không có quyền thực hiện hành động này')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    # Kiểm tra xem danh mục có công việc không
    if Task.query.filter_by(category_id=category_id).first():
        flash('Không thể xóa danh mục đang có công việc')
        return redirect(url_for('manage_categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Đã xóa danh mục!')
    return redirect(url_for('manage_categories'))


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)