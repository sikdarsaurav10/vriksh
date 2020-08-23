from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from pyfcm import FCMNotification
from web.config import Config
app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'Website.login_web'
login_manager.login_message_category = 'info'
push_service_customer = FCMNotification(api_key=app.config["PUSH_API_KEY_CUSTOMER"])
push_service_vendor = FCMNotification(api_key=app.config["PUSH_API_KEY_VENDOR"])
push_service_driver = FCMNotification(api_key=app.config["PUSH_API_KEY_DRIVER"])


import web.routes
import web.website.routes
from web.website.views import website
from web.superAdminApi.routes import admin
from web.vendorApi.routes import vendor
from web.deliveryBoyApi.routes import delivery
from web.customerApi.routes import customer


app.register_blueprint(website)
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(vendor, url_prefix="/api/vendor")
app.register_blueprint(delivery, url_prefix="/api/delivery_boy")
app.register_blueprint(customer, url_prefix="/api/customer")
