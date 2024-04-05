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
alb_ec2 = Blueprint('alb_ec2', __name__, template_folder="templates/alb_ec2")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@alb_ec2.route('/tf_exec/alb_ec2', methods=['GET'])
@login_required
def tf_exec_alb_ec2():
    return render_template('alb_ec2/alb_ec2.html')

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
@alb_ec2.route('/tf_exec/alb_ec2/alb_ec2_create_tf_workspace', methods=['GET', 'POST'])
def alb_ec2_create_tf_workspace():
    if request.method == 'POST':
        # フォームから入力された情報を取得
        workspace_name = request.form['workspace_name']

        # デフォルトリージョンと出力形式を設定
        try:
            # ワークスペースの作成
            subprocess.run(['terraform', 'workspace', 'new', workspace_name], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', check=True)
            flash(f'Terraform Workspace "{workspace_name}"が作成されました', 'success')
        except Exception as e:
            flash(f'Workspaceの作成中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('alb_ec2.alb_ec2_create_tf_workspace'))
    
    workspaces = alb_ec2_get_terraform_workspaces()
    active_workspace = alb_ec2_get_active_workspace()
    return render_template('alb_ec2/create_tf_workspace.html', workspaces=workspaces, active_workspace=active_workspace)

##アクティブなTerraform Workspaceの切り替え
@alb_ec2.route('/tf_exec/alb_ec2/switch_workspace', methods=['POST'])
def alb_ec2_switch_workspace():
    if request.method == 'POST':
        selected_workspace = request.form['selected_workspace']
        try:
            subprocess.run(['terraform', 'workspace', 'select', selected_workspace], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', check=True)
            flash(f'アクティブなワークスペースを {selected_workspace} に切り替えました', 'success')
        except Exception as e:
            flash(f'ワークスペースの切り替え中にエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('alb_ec2.alb_ec2_create_tf_workspace'))

##Terraform Workspaceの一覧を取得
def alb_ec2_get_terraform_workspaces():
    try:
        result = subprocess.run(['terraform', 'workspace', 'list'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        workspaces = result.stdout.strip().split('\n')
        return workspaces
    except Exception as e:
        flash(f'Terraformワークスペースの一覧取得中にエラーが発生しました: {str(e)}', 'error')
        return []

##Activeなワークスペースを取得
def alb_ec2_get_active_workspace():
    try:
        result = subprocess.run(['terraform', 'workspace', 'show'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        active_workspace = result.stdout.strip()
        return active_workspace
    except Exception as e:
        flash(f'アクティブなワークスペースの取得中にエラーが発生しました: {str(e)}', 'error')
        return None

##Terraform Init実行機能
@alb_ec2.route('/tf_exec/alb_ec2/tf_init', methods=['POST', 'GET'])
@login_required
def alb_ec2_tf_init():
    if request.method == 'POST':
        project_id = request.form['project_id']
        project = Project.query.get(project_id)
        if project:
            try:
                # terraform initを実行
                init_result = subprocess.run(['terraform', 'init'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Terraform initの出力を整形してファイルに書き込む
                formatted_output = format_terraform_output(init_result.stdout)

                # Terraform initの出力をファイルに書き込む
                # プロジェクトIDをファイル名に付与してファイルに書き込む
                init_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/init_output_{project_id}.html'
                # with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/init_output.html', 'w') as init_output_file:
                with open(init_output_file_path, 'w') as init_output_file:
                    init_output_file.write(formatted_output)
                
                # ユーザーがログインしていることを確認し、ログインしていればuser_idを取得
                if current_user.is_authenticated:
                    user_id = current_user.id
                    # new_execution = TerraformExecution(output_path='/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/init_output.html', project=project, user_id=user_id)
                    new_execution = TerraformExecution(output_path=init_output_file_path, project=project, user_id=user_id)
                    db.session.add(new_execution)
                    db.session.commit()

                flash('Initが成功しました', 'success')
                return render_template('alb_ec2/alb_ec2_tf_init.html')

            except subprocess.CalledProcessError as e:
                # エラーメッセージを整形してファイルに書き込む
                error_output = e.stderr.decode('utf-8')
                formatted_error_output = format_terraform_output(error_output)

                # with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/init_output.html', 'w') as init_output_file:
                #     init_output_file.write(formatted_error_output)
                                # プロジェクトIDをファイル名に付与してエラー出力をファイルに書き込む
                error_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/init_output_error_{project_id}.html'
                with open(error_output_file_path, 'w') as error_output_file:
                    error_output_file.write(formatted_error_output)

                flash('Initに失敗しました。実行結果を確認してください', 'error')
                return render_template('alb_ec2/alb_ec2_tf_init.html')
    
    active_workspace = alb_ec2_get_active_workspace()
    user_projects = current_user.projects
    return render_template('alb_ec2/alb_ec2_tf_init.html', active_workspace=active_workspace, user_projects=user_projects)

# プロジェクトの init_output 表示ルート
@alb_ec2.route('/view_project_init_output/<int:project_id>')
@login_required
def view_project_init_output(project_id):
    project = Project.query.get(project_id)

    if project:
        try:
            # 最新の TerraformExecution レコードを取得
            latest_execution = TerraformExecution.query.filter_by(project_relation=project).order_by(TerraformExecution.timestamp.desc()).first()

            if latest_execution:
                output_path_with_project_id = f"{latest_execution.output_path}"
                # with open(latest_execution.output_path, 'r') as init_output_file:
                with open(output_path_with_project_id, 'r') as init_output_file:
                    init_output = init_output_file.read()
                #return render_template('alb_ec2/init_output_.html', init_output=init_output)
                return render_template(f'alb_ec2/init_output_{project_id}.html', init_output=init_output)
            else:
                flash('実行結果が見つかりません', 'error')
                return redirect(url_for('dashboard_func.dashboard'))
        except FileNotFoundError:
            flash('実行結果ファイルが見つかりません', 'error')
            return redirect(url_for('dashboard_func.dashboard'))
    else:
        flash('プロジェクトが見つかりません', 'error')
        return redirect(url_for('dashboard_func.dashboard'))

##Terraform Plan 実行機能
@alb_ec2.route('/tf_exec/alb_ec2/tf_plan', methods=['POST', 'GET'])
@login_required
def alb_ec2_tf_plan():
    if request.method == 'POST':
        project_id = request.form['project_id']
        project = Project.query.get(project_id)
        if project:
            try:
                UPLOAD_DIR = '/home/'
                public_key = request.form.get('public_key')
                if public_key:
                    # セキュアなファイル名を生成して保存
                    new_filename = 'example.pub'
                    save_path = os.path.join(UPLOAD_DIR, new_filename)
                    with open(save_path, 'w') as f:
                        f.write(public_key)

                ##terraform.tfvarsの作成
                project_name = request.form.get('project_name')
                env = request.form.get('env')
                access_key = request.form.get('aws_access_key')
                secret_key = request.form.get('aws_secret_key')
                project_name = request.form.get('project_name')
                operation_sg_1 = request.form.get('operation_sg_1')
                operation_sg_2 = request.form.get('operation_sg_2')
                operation_sg_3 = request.form.get('operation_sg_3')
                count_number = request.form.get('count_number')
                ami = request.form.get('ami')
                instance_type = request.form.get('instance_type')
                volume_type = request.form.get('volume_type')
                volume_size = request.form.get('volume_size')

                tf_vars = {
                    "general_config": {
                        "project_name": project_name,
                        "env": env
                    },
                    "access_key": access_key,
                    "secret_key": secret_key,
                    "operation_sg_1_cidr": [operation_sg_1],
                    "operation_sg_2_cidr": [operation_sg_2],
                    "operation_sg_3_cidr": [operation_sg_3],
                    "count_number": count_number,
                    "ami": ami,
                    "instance_type": instance_type,
                    "volume_type": volume_type,
                    "volume_size": volume_size
                }

                with open('/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev/terraform.tfvars.json', 'w') as f:
                    json.dump(tf_vars, f)
        
                # terraform planを実行
                plan_result = subprocess.run(['terraform', 'plan'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Terraform planの出力を整形してファイルに書き込む
                formatted_output = format_terraform_output(plan_result.stdout)

                # Terraform planの出力をファイルに書き込む
                plan_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/plan_output_{project_id}.html'
                #with open(f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/plan_output_{project_id}.html', 'w') as plan_output_file:
                with open(plan_output_file_path, 'w') as plan_output_file:
                    plan_output_file.write(formatted_output)

                if current_user.is_authenticated:
                    user_id = current_user.id
                    #new_execution = TerraformExecution(output_path='/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/plan_output.html', project=project, user_id=user_id)
                    new_execution = TerraformExecution(output_path=plan_output_file_path, project=project, user_id=user_id)
                    db.session.add(new_execution)
                    db.session.commit()

                    flash('Planが成功しました', 'success')
                    return render_template('alb_ec2/alb_ec2_tf_plan.html')

            except subprocess.CalledProcessError as e:
                # エラーメッセージを整形してファイルに書き込む
                error_output = e.stderr.decode('utf-8')
                formatted_error_output = format_terraform_output(error_output)

                #with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/plan_output.html', 'w') as plan_output_file:
                #    plan_output_file.write(formatted_error_output)

                error_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/plan_output_error_{project_id}.html'
                with open(error_output_file_path, 'w') as error_output_file:
                    error_output_file.write(formatted_error_output)


                flash('Planに失敗しました。実行結果を確認してください', 'error')
                return render_template('alb_ec2/alb_ec2_tf_plan.html')
            
    active_workspace = alb_ec2_get_active_workspace()
    user_projects = current_user.projects
    return render_template('alb_ec2/alb_ec2_tf_plan.html', active_workspace=active_workspace, user_projects=user_projects)

# プロジェクトの plan_output 表示ルート
@alb_ec2.route('/view_project_plan_output/<int:project_id>')
@login_required
def view_project_plan_output(project_id):
    project = Project.query.get(project_id)

    if project:
        try:
            # 最新の TerraformExecution レコードを取得
            latest_execution = TerraformExecution.query.filter_by(project_relation=project).order_by(TerraformExecution.timestamp.desc()).first()

            if latest_execution:
                output_path_with_project_id = f"{latest_execution.output_path}"
                with open(output_path_with_project_id, 'r') as plan_output_file:
                    plan_output = plan_output_file.read()
                    # with open(output_filepath, 'r') as plan_output_file:
                    #     plan_output = plan_output_file.read()
                return render_template(f'alb_ec2/plan_output_{project_id}.html', plan_output=plan_output)
            else:
                flash('実行結果が見つかりません', 'error')
                return redirect(url_for('dashboard_func.dashboard'))
        except FileNotFoundError:
            flash('実行結果ファイルが見つかりません', 'error')
            return redirect(url_for('dashboard_func.dashboard'))
    else:
        flash('プロジェクトが見つかりません', 'error')
        return redirect(url_for('dashboard_func.dashboard'))

##Terraform Apply 実行機能
@alb_ec2.route('/tf_exec/alb_ec2/tf_apply', methods=['POST', 'GET'])
@login_required
def alb_ec2_tf_apply():
    if request.method == 'POST':
        project_id = request.form['project_id']
        project = Project.query.get(project_id)
        if project:
            try:
                UPLOAD_DIR = '/home/'
                public_key = request.form.get('public_key')
                if public_key:
                    # セキュアなファイル名を生成して保存
                    new_filename = 'example.pub'
                    save_path = os.path.join(UPLOAD_DIR, new_filename)
                    with open(save_path, 'w') as f:
                        f.write(public_key)

                ##terraform.tfvarsの作成
                project_name = request.form.get('project_name')
                env = request.form.get('env')
                access_key = request.form.get('aws_access_key')
                secret_key = request.form.get('aws_secret_key')
                project_name = request.form.get('project_name')
                operation_sg_1 = request.form.get('operation_sg_1')
                operation_sg_2 = request.form.get('operation_sg_2')
                operation_sg_3 = request.form.get('operation_sg_3')
                count_number = request.form.get('count_number')
                ami = request.form.get('ami')
                instance_type = request.form.get('instance_type')
                volume_type = request.form.get('volume_type')
                volume_size = request.form.get('volume_size')

                tf_vars = {
                    "general_config": {
                        "project_name": project_name,
                        "env": env
                    },
                    "access_key": access_key,
                    "secret_key": secret_key,
                    "operation_sg_1_cidr": [operation_sg_1],
                    "operation_sg_2_cidr": [operation_sg_2],
                    "operation_sg_3_cidr": [operation_sg_3],
                    "count_number": count_number,
                    "ami": ami,
                    "instance_type": instance_type,
                    "volume_type": volume_type,
                    "volume_size": volume_size
                }

                with open('/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev/terraform.tfvars.json', 'w') as f:
                    json.dump(tf_vars, f)
        
                # terraform applyを実行
                apply_result = subprocess.run(['terraform', 'apply', '-auto-approve'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Terraform Applyの出力を整形してファイルに書き込む
                formatted_output = format_terraform_output(apply_result.stdout)

                # Terraform Apllyの出力をファイルに書き込む
                apply_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/apply_output_{project_id}.html'
                with open(apply_output_file_path, 'w') as apply_output_file:
                    apply_output_file.write(formatted_output)
                #with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/apply_output.html', 'w') as apply_output_file:
                #    apply_output_file.write(formatted_output)

                if current_user.is_authenticated:
                    user_id = current_user.id
                    #new_execution = TerraformExecution(output_path='/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/apply_output.html', project=project, user_id=user_id)
                    new_execution = TerraformExecution(output_path=apply_output_file_path, project=project, user_id=user_id)
                    db.session.add(new_execution)
                    db.session.commit()

                    flash('Applyが成功しました', 'success')
                    return render_template('alb_ec2/alb_ec2_tf_apply.html')

            except subprocess.CalledProcessError as e:
                # エラーメッセージを整形してファイルに書き込む
                error_output = e.stderr.decode('utf-8')
                formatted_error_output = format_terraform_output(error_output)

                #with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/apply_output.html', 'w') as apply_output_file:
                #    apply_output_file.write(formatted_error_output)
                error_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/apply_output_error_{project_id}.html'
                with open(error_output_file_path, 'w') as error_output_file:
                    error_output_file.write(formatted_error_output)

                flash('Applyに失敗しました。実行結果を確認してください', 'error')
                return render_template('alb_ec2/alb_ec2_tf_apply.html')
    
    active_workspace = alb_ec2_get_active_workspace()
    user_projects = current_user.projects
    return render_template('alb_ec2/alb_ec2_tf_apply.html', active_workspace=active_workspace, user_projects=user_projects)

# プロジェクトの apply_output 表示ルート
@alb_ec2.route('/view_project_apply_output/<int:project_id>')
@login_required
def view_project_apply_output(project_id):
    project = Project.query.get(project_id)

    if project:
        try:
            # 最新の TerraformExecution レコードを取得
            latest_execution = TerraformExecution.query.filter_by(project_relation=project).order_by(TerraformExecution.timestamp.desc()).first()

            if latest_execution:
                output_path_with_project_id = f"{latest_execution.output_path}"
                #with open(latest_execution.output_path, 'r') as apply_output_file:
                    #apply_output = apply_output_file.read()
                with open(output_path_with_project_id, 'r') as apply_output_file:
                    apply_output = apply_output_file.read()
                #return render_template('alb_ec2/apply_output.html', apply_output=apply_output)
                return render_template(f'alb_ec2/apply_output_{project_id}.html', apply_output=apply_output)
            else:
                flash('実行結果が見つかりません', 'error')
                return redirect(url_for('dashboard_func.dashboard'))
        except FileNotFoundError:
            flash('実行結果ファイルが見つかりません', 'error')
            return redirect(url_for('dashboard_func.dashboard'))
    else:
        flash('プロジェクトが見つかりません', 'error')
        return redirect(url_for('dashboard_func.dashboard'))

##Terraform Destroy 実行機能
@alb_ec2.route('/tf_exec/alb_ec2/tf_destroy', methods=['POST', 'GET'])
@login_required
def alb_ec2_tf_destroy():
    if request.method == 'POST':
        project_id = request.form['project_id']
        project = Project.query.get(project_id)
        if project:
            try:
                UPLOAD_DIR = '/home/'
                public_key = request.form.get('public_key')
                if public_key:
                    # セキュアなファイル名を生成して保存
                    new_filename = 'example.pub'
                    save_path = os.path.join(UPLOAD_DIR, new_filename)
                    with open(save_path, 'w') as f:
                        f.write(public_key)

                ##terraform.tfvarsの作成
                project_name = request.form.get('project_name')
                env = request.form.get('env')
                access_key = request.form.get('aws_access_key')
                secret_key = request.form.get('aws_secret_key')
                project_name = request.form.get('project_name')
                operation_sg_1 = request.form.get('operation_sg_1')
                operation_sg_2 = request.form.get('operation_sg_2')
                operation_sg_3 = request.form.get('operation_sg_3')
                count_number = request.form.get('count_number')
                ami = request.form.get('ami')
                instance_type = request.form.get('instance_type')
                volume_type = request.form.get('volume_type')
                volume_size = request.form.get('volume_size')

                tf_vars = {
                    "general_config": {
                        "project_name": project_name,
                        "env": env
                    },
                    "access_key": access_key,
                    "secret_key": secret_key,
                    "operation_sg_1_cidr": [operation_sg_1],
                    "operation_sg_2_cidr": [operation_sg_2],
                    "operation_sg_3_cidr": [operation_sg_3],
                    "count_number": count_number,
                    "ami": ami,
                    "instance_type": instance_type,
                    "volume_type": volume_type,
                    "volume_size": volume_size
                }

                with open('/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev/terraform.tfvars.json', 'w') as f:
                    json.dump(tf_vars, f)
        
                # terraform destoryを実行
                destroy_result = subprocess.run(['terraform', 'destroy', '-auto-approve'], cwd='/var/www/vhosts/terraform-gui.com/public_html/terraform_dir/alb_ec2_terraform/env/dev', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Terraform Destroyの出力を整形してファイルに書き込む
                formatted_output = format_terraform_output(destroy_result.stdout)

                # Terraform Destroyの出力をファイルに書き込む
                #with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/destroy_output.html', 'w') as destroy_output_file:
                #    destroy_output_file.write(formatted_output)
                destroy_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/destroy_output_{project_id}.html'
                with open(destroy_output_file_path, 'w') as destroy_output_file:
                    destroy_output_file.write(formatted_output)

                if current_user.is_authenticated:
                    user_id = current_user.id
                    #new_execution = TerraformExecution(output_path='/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/destroy_output.html', project=project, user_id=user_id)
                    new_execution = TerraformExecution(output_path=destroy_output_file_path, project=project, user_id=user_id)
                    db.session.add(new_execution)
                    db.session.commit()

                    flash('Destroyが成功しました', 'success')
                    return render_template('alb_ec2/alb_ec2_tf_destroy.html')

            except subprocess.CalledProcessError as e:
                # エラーメッセージを整形してファイルに書き込む
                error_output = e.stderr.decode('utf-8')
                formatted_error_output = format_terraform_output(error_output)

                #with open('/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/destroy_output.html', 'w') as destroy_output_file:
                #    destroy_output_file.write(formatted_error_output)

                error_output_file_path = f'/var/www/vhosts/terraform-gui.com/public_html/blog/templates/alb_ec2/destroy_output_error_{project_id}.html'
                with open(error_output_file_path, 'w') as error_output_file:
                    error_output_file.write(formatted_error_output)

                flash('Destroyに失敗しました。実行結果を確認してください', 'error')
                return render_template('alb_ec2/alb_ec2_tf_destroy.html')

    active_workspace = alb_ec2_get_active_workspace()
    user_projects = current_user.projects
    return render_template('alb_ec2/alb_ec2_tf_destroy.html', active_workspace=active_workspace, user_projects=user_projects)

# プロジェクトの destroy_output 表示ルート
@alb_ec2.route('/view_project_destroy_output/<int:project_id>')
@login_required
def view_project_destroy_output(project_id):
    project = Project.query.get(project_id)

    if project:
        try:
            # 最新の TerraformExecution レコードを取得
            latest_execution = TerraformExecution.query.filter_by(project_relation=project).order_by(TerraformExecution.timestamp.desc()).first()

            if latest_execution:
                output_path_with_project_id = f"{latest_execution.output_path}"
                #with open(latest_execution.output_path, 'r') as destroy_output_file:
                with open(output_path_with_project_id, 'r') as destroy_output_file:
                    destroy_output = destroy_output_file.read()
                #return render_template('alb_ec2/destroy_output.html', destroy_output=destroy_output)
                return render_template(f'alb_ec2/destroy_output_{project_id}.html', destroy_output=destroy_output)
            else:
                flash('実行結果が見つかりません', 'error')
                return redirect(url_for('dashboard_func.dashboard'))
        except FileNotFoundError:
            flash('実行結果ファイルが見つかりません', 'error')
            return redirect(url_for('dashboard_func.dashboard'))
    else:
        flash('プロジェクトが見つかりません', 'error')
        return redirect(url_for('dashboard_func.dashboard'))