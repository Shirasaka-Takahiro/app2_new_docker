from flask import render_template, request, redirect, url_for, flash, Blueprint
from blog import app
from blog import db
from blog.models.user import User
from blog.models.user import Project
from blog.models.user import TerraformExecution
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from blog import login_manager
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import subprocess
import yaml
import os

## Create Blueprint Object
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
        ANSIBLE_EXEC_DIR = f'/var/www/vhosts/terraform-gui.com/public_html/ansible_dir/{server_name}/'

        try:
            if playbooks:
                playbook_file = 'playbook.yml'
                playbook_save_path = os.path.join(ANSIBLE_EXEC_DIR, playbook_file)
                with open(playbook_save_path, 'w') as f:
                    f.write(playbooks)
            
            if inventory:
                inventory_file = 'hosts'
                inventory_save_path = os.path.join(ANSIBLE_EXEC_DIR, inventory_file)
                with open(inventory_save_path, 'w') as f:
                    f.write(inventory)
            
            if private_key:
                private_key_file = 'keys/user.key'
                private_key_save_path = os.path.join(ANSIBLE_EXEC_DIR, private_key_file)
                with open(private_key_save_path, 'w') as f:
                    f.write(private_key)

            if group_vars:
                group_vars_file = 'group_vars/all.yml'
                group_vars_save_path = os.path.join(ANSIBLE_EXEC_DIR, group_vars_file)
                with open(group_vars_save_path, 'w') as f:
                    f.write(group_vars)
            
            command = ['ansible-playbook']
            if inventory:
                command.extend(['-i', inventory_save_path])
            if private_key:
                command.extend(['--private-key', private_key_save_path])
            if playbooks:
                command.append(playbook_save_path)

            result = subprocess.run(
                command,
                cwd=f'/var/www/vhosts/terraform-gui.com/public_html/ansible_dir/{server_name}/',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,  # 標準入力を設定
                input=b'yes\n'  # 自動的に"Yes"を入力する
            )

            if result.returncode == 0:
                flash('Ansible provisioning succeeded!', 'success')
            else:
                flash('Ansible provisioning failed!', 'error')
                flash(result.stderr.decode('utf-8'), 'error')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('ansible_exec/ansible_exec.html', user=current_user)
