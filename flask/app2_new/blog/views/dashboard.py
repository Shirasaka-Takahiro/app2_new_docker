from flask import render_template, Blueprint
from blog.models.user import User
from blog import login_manager
from flask_login import login_required, current_user

##Create Blueprint Object
dashboard_func = Blueprint('dashboard_func', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Dashboard route
@dashboard_func.route('/dashboard')
@login_required
def dashboard():
    user_projects = current_user.projects
    return render_template('dashboard/dashboard.html', user_projects=user_projects)