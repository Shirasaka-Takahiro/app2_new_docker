from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog.models.user import User
from blog.models.user import Project
from blog import login_manager
from blog import db
from flask_login import login_required, current_user

##Create Blueprint Object
project_func = Blueprint('project_func', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create Project
@project_func.route('/create_project', methods=['POST', 'GET'])
@login_required
def create_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        new_project = Project(name=project_name, user=current_user)
        db.session.add(new_project)
        db.session.commit()
        flash('プロジェクトが作成されました', 'success')
        return redirect(url_for('dashboard_func.dashboard'))
    return render_template('project/project.html')
