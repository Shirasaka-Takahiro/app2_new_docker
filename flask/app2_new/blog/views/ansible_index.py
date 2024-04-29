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
ansible_index = Blueprint('ansible_index', __name__, template_folder="templates/ansible_exec")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@ansible_index.route('/ansible_index', methods=['GET'])
@login_required
def ansible_index_func():
    return render_template('ansible_exec/ansible_index.html')