from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog.models.user import User
from blog import db
from blog import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

##Create Blueprint Object
user_func = Blueprint('user_func', __name__, template_folder="templates/user")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##ユーザー認証機能
@user_func.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(
            username=username, 
            password=generate_password_hash(password, method='sha256'),
        )
        db.session.add(user)
        db.session.commit()
        flash('ユーザー登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('user/signup.html')

##Adminユーザーの追加画面
##ユーザー認証機能
@user_func.route('/signup_admin', methods=['GET', 'POST'])
def signup_admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        user = User(
            username=username, 
            password=generate_password_hash(password, method='sha256'),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        flash('ユーザー登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('user/signup_admin.html')

##ユーザー一覧画面
@user_func.route('/user_list')
@login_required
def user_list():
    # 管理者ユーザーのみがアクセスできるようにする
    if not current_user.is_admin:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('user/user_list.html', users=users)

# ユーザー詳細画面
@user_func.route('/user_detail/<int:user_id>')
@login_required
def user_detail(user_id):
    # 管理者ユーザーのみがアクセスできるようにする
    if not current_user.is_admin:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user:
        return render_template('user/user_detail.html', user=user)
    else:
        flash('指定されたユーザーが存在しません。', 'error')
        return redirect(url_for('user_list'))

# ユーザー編集画面
@user_func.route('/user_edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    # 管理者ユーザーのみがアクセスできるようにする
    if not current_user.is_admin:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if not user:
        flash('指定されたユーザーが存在しません。', 'error')
        return redirect(url_for('user_list'))

    if request.method == 'POST':
        # ユーザー情報を更新
        user.username = request.form['username']
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('ユーザー情報を更新しました。', 'success')
        return redirect(url_for('user_list'))

    return render_template('user/user_edit.html', user=user)

# ユーザー削除画面
@user_func.route('/user_delete/<int:user_id>')
@login_required
def user_delete(user_id):
    # 管理者ユーザーのみがアクセスできるようにする
    if not current_user.is_admin:
        flash('アクセス権限がありません。', 'error')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if not user:
        flash('指定されたユーザーが存在しません。', 'error')
        return redirect(url_for('user_list'))

    # ユーザーを削除
    db.session.delete(user)
    db.session.commit()
    flash('ユーザーを削除しました。', 'success')
    return redirect(url_for('user_list'))