from flask import render_template, request, redirect, url_for, flash, Blueprint
import subprocess

##Create Blueprint Object
aws_profile = Blueprint('aws_profile', __name__, template_folder="templates/aws_profile")

#AWSProfileの作成
@aws_profile.route('/create_aws_profile', methods=['GET', 'POST'])
def create_aws_profile():
    if request.method == 'POST':
        # フォームから入力された情報を取得
        profile_name = request.form['profile_name']
        aws_access_key = request.form['aws_access_key']
        aws_secret_key = request.form['aws_secret_key']
        region = request.form['region']
        output_format = request.form['output_format']

        # デフォルトリージョンと出力形式を設定
        try:
            subprocess.run([
                'aws', 'configure', 'set', 'region', region, '--profile', profile_name
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'output', output_format, '--profile', profile_name
            ])
        except Exception as e:
            flash(f'デフォルトリージョンと出力形式の設定中にエラーが発生しました: {str(e)}', 'error')

        # AWSプロファイルの作成
        try:
            subprocess.run([
                'aws', 'configure', 'set', 'aws_access_key_id', aws_access_key, '--profile', profile_name
            ])
            subprocess.run([
                'aws', 'configure', 'set', 'aws_secret_access_key', aws_secret_key, '--profile', profile_name
            ])
            flash('AWSプロファイルが作成され、デフォルトリージョンおよび出力形式が設定されました', 'success')
        except Exception as e:
            flash(f'AWSプロファイルの作成中にエラーが発生しました: {str(e)}', 'error')

        return redirect(url_for('aws_profile.create_aws_profile'))

    return render_template('aws_profile/create_aws_profile.html')