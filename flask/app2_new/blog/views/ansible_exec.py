from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog import app
from random import randint
from blog import db
from blog.models.employee import Employee
from blog.models.user import User
from blog.models.user import Project
from blog.models.user import TerraformExecution
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from blog import login_manager
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import subprocess
import os
import json
import re
import yaml

##Create Blueprint Object
ansible_exec = Blueprint('ansible_exec', __name__, template_folder="templates/ansible_exec")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@ansible_exec.route('/ansible_exec', methods=['GET', 'POST'])
@login_required
def ansible_exec_func():
    if request.method == 'POST':
        playbooks = request.form['playbooks']
        inventory = request.form['inventory']
        private_key = request.form['private_key']
        group_vars = request.form['group_vars']
        server_name = request.form['server']

        # サーバー名に応じてディレクトリを切り替える
        playbook_dir = f'/var/www/vhosts/terraform-gui.com/public_html/{server_name}/playbook.yml'

        # playbooks、inventory、private_key、group_varsの値を既存ファイルに書き換える
        with open(playbook_dir, 'r+') as f:
            data = yaml.safe_load(f)
            data['playbooks'] = playbooks
            f.seek(0)
            yaml.safe_dump(data, f, default_flow_style=False)

        inventory_path = f'/var/www/vhosts/terraform-gui.com/public_html/{server_name}/hosts'
        with open(inventory_path, 'r+') as f:
            data = yaml.safe_load(f)
            data['inventory'] = inventory
            f.seek(0)
            yaml.safe_dump(data, f, default_flow_style=False)

        private_key_path = f'/var/www/vhosts/terraform-gui.com/public_html/{server_name}/keys/user.key'
        with open(private_key_path, 'r+') as f:
            content = f.read()
            content = content.replace('{{ private_key_placeholder }}', private_key)
            f.seek(0)
            f.truncate()
            f.write(content)

        group_vars_path = f'/var/www/vhosts/terraform-gui.com/public_html/{server_name}/group_vars/all.yml'
        with open(group_vars_path, 'r+') as f:
            data = yaml.safe_load(f)
            data['group_vars'] = group_vars
            f.seek(0)
            yaml.safe_dump(data, f, default_flow_style=False)
            
        # ここでAnsibleの実行を行う
        result = subprocess.run(
            ['ansible-playbook', '-i', inventory, '--private-key', private_key, playbook_dir],
            cwd=f'/var/www/vhosts/terraform-gui.com/public_html/{server_name}/',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 実行結果を返す
        return result.stdout.decode('utf-8')

    return render_template('ansible_exec/ansible_exec.html', user=current_user)
