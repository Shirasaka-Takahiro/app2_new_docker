from flask import render_template, request, redirect, url_for, flash
from blog import app
from random import randint
from blog import db
from blog.models.employee import Employee
from blog.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from blog import login_manager
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
import subprocess, os, json, re

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    my_dict = {
        'insert_something1': 'views.pyのinsert_something1部分です。',
        'insert_something2': 'views.pyのinsert_something2部分です。',
        'test_titles': ['title1', 'title2', 'title3']
    }
    return render_template('testapp/index.html', my_dict=my_dict)

@app.route('/test')
def other1():
    return render_template('testapp/index2.html')

##じゃんけん機能
@app.route('/sampleform', methods=['GET', 'POST'])
@login_required
def sample_form():
    if request.method == 'GET':
        return render_template('testapp/sampleform.html')
    elif request.method == 'POST':
        hands = {
            '0': 'グー',
            '1': 'チョキ',
            '2': 'パー',
        }
        janken_mapping = {
            'draw': '引き分け',
            'win': '勝ち',
            'lose': '負け',
        }

        player_hand_ja = hands[request.form['janken']]
        player_hand = int(request.form['janken'])
        enemy_hand = randint(0,2)
        enemy_hand_ja = hands[str(enemy_hand)]
        if player_hand == enemy_hand:
            judgement = 'draw'
        elif (player_hand == 0 and enemy_hand == 1) or (player_hand == 1 and enemy_hand == 2) or (player_hand == 2 and enemy_hand == 0):
            judgement = 'win'
        else:
            judgement = 'lose'
        result = {
            'enemy_hand_ja': enemy_hand_ja,
            'player_hand_ja': player_hand_ja,
            'judgement': janken_mapping[judgement],
        }
        return render_template('testapp/janken_result.html', result=result)

##従業員追加機能
@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'GET':
        return render_template('testapp/add_employee.html')
    elif request.method == 'POST':
        form_name = request.form.get('name')
        form_mail = request.form.get('mail')
        form_is_remote = request.form.get('is_remote', default=False, type=bool)
        form_department = request.form.get('department')
        form_year = request.form.get('year', default=0, type=int)

        employee = Employee(
            name = form_name,
            mail = form_mail,
            is_remote = form_is_remote,
            department = form_department,
            year = form_year 
        )
        db.session.add(employee)
        db.session.commit()
        flash('従業員を追加しました。', 'success')
        return redirect(url_for('index'))

@app.route('/employees')
@login_required
def employee_list():
    employees = Employee.query.all()
    return render_template('testapp/employee_list.html', employees=employees)

@app.route('/employees/<int:id>')
@login_required
def employee_detail(id):
    employee = Employee.query.get_or_404(id)
    return render_template('testapp/employee_detail.html', employee=employee)

@app.route('/employees/<int:id>/edit', methods=['GET'])
@login_required
def employee_edit(id):
    employee = Employee.query.get(id)
    return render_template('testapp/employee_edit.html', employee=employee)

@app.route('/employees/<int:id>/update', methods=['POST'])
@login_required
def employee_update(id):
    employee = Employee.query.get(id)
    employee.name = request.form.get('name')
    employee.mail = request.form.get('mail')
    employee.is_remote = request.form.get('is_remote', default=False, type=bool)
    employee.department = request.form.get('department')
    employee.year = request.form.get('year', default=0, type=int)

    db.session.merge(employee)
    db.session.commit()
    flash('編集が完了しました。', 'success')
    return redirect(url_for('employee_list'))

@app.route('/employees/<int:id>/delete', methods=['POST'])
@login_required
def employee_delete(id):
    employee = Employee.query.get(id)
    db.session.delete(employee)
    db.session.commit()
    flash('削除が完了しました。', 'success')
    return redirect(url_for('employee_list'))

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
