import os
import secrets
from flask import request, jsonify, make_response, url_for
from web import app, mail, push_service_customer,\
    push_service_vendor, push_service_driver
from web.models import Admin, Vendor, Deliveryboy, Customer
from functools import wraps
import jwt
from flask_mail import Message
import urllib.request
import json
import requests


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # token name is x-admin-token
        # passed when admin is logged in
        if 'x-admin-token' in request.headers:
            token = request.headers['x-admin-token']

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = Admin.query\
                    .filter_by(admin_id=data['admin_id'])\
                    .first()
            except Exception:
                return jsonify({"success": "0",
                                "message": "Token not valid!!"}), 401

        # token name is x-vendor-token
        # passed when vendor is logged in
        if 'x-vendor-token' in request.headers:
            token = request.headers['x-vendor-token']

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = Vendor.query\
                    .filter_by(vendor_id=data['vendor_id'])\
                    .first()
            except Exception:
                return jsonify({"success": "0",
                                "message": "Token not valid!!"}), 401

        # token name is x-driver-token
        # passed when driver is logged in
        if 'x-driver-token' in request.headers:
            token = request.headers['x-driver-token']

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = Deliveryboy.query\
                    .filter_by(driver_id=data['driver_id'])\
                    .first()
            except Exception:
                return jsonify({"success": "0",
                                "message": "Token not valid!!"}), 401

        # token name is x-customer-token
        # passed when customer is logged in
        if 'x-customer-token' in request.headers:
            token = request.headers['x-customer-token']

            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
                current_user = Customer.query\
                    .filter_by(customer_id=data['customer_id'])\
                    .first()
            except Exception:
                return jsonify({"success": "0",
                                "message": "Token not valid!!"}), 401

        if not token:
            return make_response('Token is missing!!', 401)

        return f(current_user, *args, **kwargs)

    return decorated


def save_vendor_pic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/vendor_prof_pic/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def save_deliveryBoy_aadharpic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/deliveryBoy_aadhar_pic/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def save_deliveryBoy_profpic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/deliveryBoy_prof_pic/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def save_product_pic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/product_prof_pic/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def save_category_pic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/category_prof_pic/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def save_banner_pic(prof_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(prof_pic.filename)
    file_ext_allowed = [".jpg", ".png", ".jpeg"]
    if f_ext in file_ext_allowed:
        pic_fn = random_hex + f_ext
        pic_path = os.path.join(app.root_path,
                                'static/images/banner_pics/',
                                pic_fn)
        prof_pic.save(pic_path)
        return pic_fn
    return "Not allowed"


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your Password, visit the following link:
{url_for('Admin.reset_password_admin', token=token, _external=True)}

If you did not make this request, Please Ignore this!!
    '''
    mail.send(msg)


# select nearest vendor
def select_vendor(latitude, longitude, city):
    vendors = []

    ven = Vendor.query.filter_by(city=city).all()

    for i in ven:
        info = {}
        info["vendor_id"] = i.vendor_id
        data = "https://apis.mapmyindia.com/advancedmaps/v1/"+app.config["MAP_SERVER_KEY"]+"/distance_matrix/driving/"+str(longitude)+","+str(latitude)+";"+str(i.longitude)+","+str(i.latitude)+"?rtype=1&region=ind"
        with urllib.request.urlopen(data) as url:
            data_map = json.loads(url.read().decode())
            info["distance"] = data_map["results"]["distances"][0][1]
            info["duration"] = data_map["results"]["durations"][0][1]
        vendors.append(info)

    vendors.sort(key=sortdistance)

    return vendors


def sortdistance(val):
    return val["distance"]


# send push notification customer
def send_push_customer(title, body, registration_id):
    registration_id = registration_id
    message_title = str(title)
    message_body = str(body)
    result = push_service_customer\
        .notify_single_device(
                              registration_id=registration_id,
                              message_title=message_title,
                              message_body=message_body)
    return result


# send push notification vendor
def send_push_vendor(title, body, registration_id):
    registration_id = registration_id
    message_title = str(title)
    message_body = str(body)
    result = push_service_vendor\
        .notify_single_device(
                              registration_id=registration_id,
                              message_title=message_title,
                              message_body=message_body)
    return result


# send push notification driver
def send_push_driver(title, body, registration_id):
    registration_id = registration_id
    message_title = str(title)
    message_body = str(body)
    result = push_service_driver\
        .notify_single_device(
                              registration_id=registration_id,
                              message_title=message_title,
                              message_body=message_body)
    return result


# find out longitude and latitude
def find_coord(address):
    url = "https://outpost.mapmyindia.com/api/security/oauth/token?grant_type=client_credentials&client_id="+str(app.config["CLIENT_ID"])+"&client_secret="+str(app.config["CLIENT_SECRET"])
    url_cod = "https://atlas.mapmyindia.com/api/places/geocode?address="+str(address)

    data = find_auth_token(url)
    token = data["access_token"]

    result = lat_long(url_cod, token)

    res = [result["copResults"]["latitude"], result["copResults"]["longitude"]]

    return res


def find_auth_token(url_path):
    result = requests.post(url_path)
    return result.json()


def lat_long(url_path, token):
    headers = {'Authorization': token}
    result = requests.get(url_path, headers=headers)
    return result.json()
