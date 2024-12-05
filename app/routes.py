from flask import render_template, request, redirect, url_for, flash, Blueprint
from app import db
from .models import User, Project
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import current_app
import os
import re

routes = Blueprint('routes', __name__)

# Функция для извлечения навыков из описания проекта
def extract_skills_from_description(description):
    skills = []
    keywords = ['design', 'development', 'marketing', 'data analysis', 'ui/ux', 'python', 'javascript']
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', description, re.IGNORECASE):
            skills.append(keyword)
    return skills

# Функция для поиска пользователей с подходящими навыками
def find_matching_users(skills):
    if not skills:
        return []
    matching_users = User.query.filter(User.skills.ilike(f'%{skills[0]}%'))
    for skill in skills[1:]:
        matching_users = matching_users.filter(User.skills.ilike(f'%{skill}%'))
    return matching_users.all()

@routes.route('/', methods=['GET'])
def index():
    query = request.args.get('query')
    tag_filter = request.args.get('tag')
    sort_by = request.args.get('sort_by')

    projects_query = Project.query

    if query:
        projects_query = projects_query.filter(
            (Project.title.ilike(f'%{query}%')) |
            (Project.description.ilike(f'%{query}%')) |
            (Project.tags.ilike(f'%{query}%'))
        )

    if tag_filter:
        projects_query = projects_query.filter(Project.tags.ilike(f'%{tag_filter}%'))

    if sort_by == 'date':
        projects_query = projects_query.order_by(Project.id.desc())
    elif sort_by == 'title':
        projects_query = projects_query.order_by(Project.title.asc())

    projects = projects_query.all()

    return render_template('index.html', projects=projects)

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash('You have successfully registered! To start, please complete your profile!', 'success')
        return redirect(url_for('routes.index'))

    return render_template('register.html')

@routes.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

@routes.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.bio = request.form['bio']
        current_user.skills = request.form['skills']
        current_user.field_of_work = request.form['field_of_work']

        avatar = request.files.get('avatar')
        if avatar:
            filename = secure_filename(avatar.filename)
            avatar_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)
            avatar_path = os.path.join(avatar_folder, filename)
            try:
                avatar.save(avatar_path)
                current_user.avatar = filename
                print(f"Avatar saved successfully: {avatar_path}")
            except Exception as e:
                print(f"Failed to save avatar: {e}")

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('routes.profile', user_id=current_user.id))

    return render_template('edit_profile.html', user=current_user)

@routes.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('routes.change_password'))

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('routes.change_password'))

        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('routes.profile', user_id=current_user.id))

    return render_template('change_password.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('If you have not yet completed your profile, we recommend do it so you can be found and contacted', 'success')
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.login'))

@routes.route('/project/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        creator_id = current_user.id

        image_file = request.files.get('images')
        image_filename = None
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'projects', 'images')
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join(image_folder, secure_filename(image_file.filename))
            try:
                image_file.save(image_path)
                print(f"Image saved successfully: {image_path}")
            except Exception as e:
                print(f"Failed to save image: {e}")

        project = Project(
            title=title,
            description=description,
            tags=tags,
            creator_id=creator_id,
            image=image_filename
        )
        db.session.add(project)
        db.session.commit()

        print(f"Project created with image: {project.image}")

        flash('Project created successfully!', 'success')
        return redirect(url_for('routes.index'))

    return render_template('create_project.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.creator_id != current_user.id:
        flash('You are not authorized to edit this project.', 'danger')
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        project.title = request.form['title']
        project.description = request.form['description']
        project.tags = request.form['tags']

        image_file = request.files.get('images')
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_folder = os.path.join('static', 'uploads', 'projects', 'images')
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join(image_folder, image_filename)

            print(f"Saving new image to: {image_path}")

            try:
                image_file.save(image_path)
                print(f"Image saved successfully at: {image_path}")
                project.image = image_filename
            except Exception as e:
                print(f"Error saving new image: {e}")

        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('routes.index'))

    return render_template('edit_project.html', project=project)

@routes.route('/project/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project.creator_id != current_user.id:
        flash('You are not authorized to delete this project.', 'danger')
        return redirect(url_for('routes.index'))

    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('routes.index'))

@routes.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query')
    skill_filter = request.args.get('skill')

    users_query = User.query

    if query:
        users_query = users_query.filter(
            (User.name.ilike(f'%{query}%')) |
            (User.skills.ilike(f'%{query}%')) |
            (User.field_of_work.ilike(f'%{query}%'))
        )

    if skill_filter:
        users_query = users_query.filter(User.skills.ilike(f'%{skill_filter}%'))

    users = users_query.all()

    return render_template('search_users.html', users=users)

@routes.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    skills = extract_skills_from_description(project.description)
    suggested_users = find_matching_users(skills)
    return render_template('project_details.html', project=project, suggested_users=suggested_users)

@routes.route('/project/<int:project_id>/edit_details', methods=['POST'])
@login_required
def edit_project_detail(project_id):
    project = Project.query.get_or_404(project_id)

    if project.creator_id != current_user.id:
        flash('You are not authorized to edit this project.', 'danger')
        return redirect(url_for('routes.project_detail', project_id=project.id))

    project.project_detail = request.form['details']
    db.session.commit()
    flash('Project details updated successfully!', 'success')
    return redirect(url_for('routes.project_detail', project_id=project.id))