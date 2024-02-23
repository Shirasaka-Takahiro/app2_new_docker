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

##Create Blueprint Object
alb_ec2_route53 = Blueprint('alb_ec2_route53', __name__, template_folder="templates/alb_ec2_route53")

@app.route('/tf_exec/alb_ec2_route53', methods=['GET'])
@login_required
def tf_exec_alb_ec2_route53():
    return render_template('testapp/alb_ec2_route53.html')

def format_terraform_output(output):
    # 改行で分割
    lines = output.decode('utf-8').split('\n')
    formatted_lines = []
    for line in lines:
        # ANSIエスケープコードを削除
        line = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', line)
        # 空白を削除してから行を追加
        formatted_lines.append(line.strip())
    
    # 整形された行を連結して整形された出力を生成
    formatted_output = "<p>{}</p>".format('</p><p>'.join(formatted_lines))
    return formatted_output

#Terraform Workspaceの作成
@app.route('/tf_exec/alb_ec2/alb_ec2_route53_create_tf_workspace', methods=['GET', 'POST'])
def alb_ec2_route53_create_tf_workspace():
    if request.method == 'POST':
        # フォームから入力された情報を取得
        workspace_name = request.form['workspace_name']

        # デフォルトリージョンと出力形式を設定
        try:
            # ワークスペースの作成
            subprocess.run(['terraform', 'workspace', 'new', workspace_name], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_route53_terraform/env/dev', check=True)
            flash(f'Terraform Workspace "{workspace_name}"が作成されました', 'success')
        except Exception as e:
            flash(f'Workspaceの作成中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('alb_ec2_route53_create_tf_workspace'))
    
    workspaces = alb_ec2_route53_get_terraform_workspaces()
    active_workspace = alb_ec2_route53_get_active_workspace()
    return render_template('testapp/create_tf_workspace.html', workspaces=workspaces, active_workspace=active_workspace)

##アクティブなTerraform Workspaceの切り替え
@app.route('/tf_exec/alb_ec2_route53/switch_workspace', methods=['POST'])
def alb_ec2_route53_switch_workspace():
    if request.method == 'POST':
        selected_workspace = request.form['selected_workspace']
        try:
            subprocess.run(['terraform', 'workspace', 'select', selected_workspace], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_route53_terraform/env/dev', check=True)
            flash(f'アクティブなワークスペースを {selected_workspace} に切り替えました', 'success')
        except Exception as e:
            flash(f'ワークスペースの切り替え中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('alb_ec2_route53_create_tf_workspace'))

##Terraform Workspaceの一覧を取得
def alb_ec2_route53_get_terraform_workspaces():
    try:
        result = subprocess.run(['terraform', 'workspace', 'list'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_route53_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        workspaces = result.stdout.strip().split('\n')
        return workspaces
    except Exception as e:
        flash(f'Terraformワークスペースの一覧取得中にエラーが発生しました: {str(e)}', 'error')
        return []

##Activeなワークスペースを取得
def alb_ec2_route53_get_active_workspace():
    try:
        result = subprocess.run(['terraform', 'workspace', 'show'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_route53_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        active_workspace = result.stdout.strip()
        return active_workspace
    except Exception as e:
        flash(f'アクティブなワークスペースの取得中にエラーが発生しました: {str(e)}', 'error')
        return None

@app.route('/tf_exec/alb_ec2_route53/alb_ec2_route53_tf_init', methods=['POST', 'GET'])
@login_required
def alb_ec2_route53_tf_init():
    active_workspace = alb_ec2_route53_get_active_workspace()
    if request.method == 'POST':
        try:
            # terraform initを実行
            init_result = subprocess.run(['terraform', 'init'], cwd='/home/vagrant/app2_new/terrafomr_dir/alb_ec2_route53_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Terraform initの出力を整形してファイルに書き込む
            formatted_output = format_terraform_output(init_result.stdout)

            # Terraform initの出力をファイルに書き込む
            with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/testapp/alb_ec2_route53_init_output.html', 'w') as init_output_file:
                init_output_file.write(formatted_output)

            flash('Initが成功しました', 'success')
            return render_template('testapp/tf_init.html')

        except subprocess.CalledProcessError as e:
            # エラーメッセージを整形してファイルに書き込む
            error_output = e.stderr.decode('utf-8')
            formatted_error_output = format_terraform_output(error_output)

            with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/testapp/alb_ec2_route53_init_output.html', 'w') as init_output_file:
                init_output_file.write(formatted_error_output)

            flash('Initに失敗しました。実行結果を確認してください', 'error')
            return render_template('testapp/tf_init.html')
    active_workspace = alb_ec2_route53_get_active_workspace()
    return render_template('testapp/tf_init.html', active_workspace=active_workspace)

##Terraform Initの実行結果確認
@app.route('/tf_exec/alb_ec2_route53/view_init_output')
@login_required
def alb_ec2_route53_view_init_output():
    try:
        with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/testapp/init_output.html', 'r') as init_output_file:
            init_output = init_output_file.read()
        return render_template('testapp/alb_ec2_route53_init_output.html', init_output=init_output)
    except FileNotFoundError:
        flash('実行結果ファイルが見つかりません', 'error')
        return redirect(url_for('tf_init'))
