from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

##Create Blueprint Object
login_func = Blueprint('login_func', __name__, template_folder="templates/login")

@login_func.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインに成功しました。', 'success')
            return redirect(url_for('index'))
        else:
            flash('ログインに失敗しました。ユーザー名またはパスワードが正しくありません。', 'error')
            return redirect(url_for('index'))
    else:
        return render_template('login/login.html')