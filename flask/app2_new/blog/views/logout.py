from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog.models.user import User
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

##Create Blueprint Object
logout_func = Blueprint('logout_func', __name__)

@logout_func.route('/logout')
def logout():
    logout_user()
    flash('ログアウトに成功しました。', 'success')
    return redirect(url_for('index'))