from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('blog.config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from .models import employee, user

login_manager = LoginManager()
login_manager.init_app(app)

import blog.views.views

##Login用Blueprint
from blog.views.login import login_func
app.register_blueprint(login_func)

##Logout用Blueprint
from blog.views.logout import logout_func
app.register_blueprint(logout_func)

##User用Blueprint
from blog.views.user import user_func
app.register_blueprint(user_func)

##Project用Blueprint
from blog.views.project import project_func
app.register_blueprint(project_func)

##Dashboard用Blueprint
from blog.views.dashboard import dashboard_func
app.register_blueprint(dashboard_func)

##AWS Profile用Blueprint
from blog.views.aws_profile import aws_profile
app.register_blueprint(aws_profile)

##tf_exec用Blueprint
from blog.views.tf_exec import tf_exec_func
app.register_blueprint(tf_exec_func)

##ALB + EC2用Blueprint
from blog.views.alb_ec2 import alb_ec2
app.register_blueprint(alb_ec2)

##ALB + EC2 + Route53用Blueprint
from blog.views.alb_ec2_route53 import alb_ec2_route53
app.register_blueprint(alb_ec2_route53)

##ALB + EC2 + RDS
from blog.views.alb_ec2_rds import alb_ec2_rds
app.register_blueprint(alb_ec2_rds)