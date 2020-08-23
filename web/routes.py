from flask import request, jsonify, url_for
from web import app, db
from web.models import Admin, Vendor, Products,\
    Vendor_products, Deliveryboy, Customer, Category,\
    Promotionalcodes, Bannerimages, Productratings,\
    Cityandcharge
from werkzeug.security import check_password_hash
import jwt
import datetime


# login for super admin
@app.route('/login/admin', methods=['POST'])
def login_admin():

    auth = request.get_json()

    if not auth or not auth["email"] or not auth["password"]:
        return jsonify({"success": "0",
                        "message": "Email or password cannot be empty"})

    user = Admin.query.filter_by(email=auth["email"]).first()

    if not user:
        return jsonify({"success": "0", "message": "Admin not present"})

    if check_password_hash(user.password, auth["password"]):
        token = jwt.encode(
            {'admin_id': user.admin_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            app.config['SECRET_KEY'])

        return jsonify({"success": "1", "message": "Login Successful!",
                        "token": token.decode('UTF-8')})

    return jsonify({"success": "0", "message": "Could not verify"})


# login for the vendor
@app.route('/login/vendor', methods=['POST'])
def login_vendor():

    auth = request.get_json()

    if not auth or not auth["email"] or not auth["password"]:
        return jsonify({"success": "0",
                        "message": "Email or password cannot be empty"})

    user = Vendor.query.filter_by(email=auth["email"].lower()).first()

    if not user:
        return jsonify({"success": "0", "message": "Vendor not present"})

    if check_password_hash(user.password, auth["password"]):
        token = jwt.encode(
            {'vendor_id': user.vendor_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            app.config['SECRET_KEY'])

        if "registration_id" in auth:
            user.device_id = auth["registration_id"]

            db.session.commit()

            return jsonify({"success": "1", "message": "Login Successful!",
                            "token": token.decode('UTF-8'),
                            "name": user.name,
                            "id": "updated"})

        return jsonify({"success": "1", "message": "Login Successful!",
                        "token": token.decode('UTF-8'),
                        "name": user.name})

    return jsonify({"success": "0", "message": "Could not verify"})


# login for the delivery boy
@app.route('/login/delivery_boy', methods=['POST'])
def login_deliveryBoy():

    auth = request.get_json()

    if not auth or not auth["contact"] or not auth["password"]:
        return jsonify({"success": "0",
                        "message": "Phone Number or password cannot be empty"})

    user = Deliveryboy.query.filter_by(contact=auth["contact"]).first()

    if not user:
        return jsonify({"success": "0", "message": "Delivery Boy not present"})

    if check_password_hash(user.password, auth["password"]):
        token = jwt.encode(
            {'driver_id': user.driver_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            app.config['SECRET_KEY'])

        if "registration_id" in auth:
            user.device_id = auth["registration_id"]

            db.session.commit()

            return jsonify({"success": "1", "message": "Login Successful!",
                            "token": token.decode('UTF-8'),
                            "name": user.name,
                            "id": "updated"})

        return jsonify({"success": "1", "message": "Login Successful!",
                        "token": token.decode('UTF-8'),
                        "name": user.name})

    return jsonify({"success": "0", "message": "Could not verify"})


# login for the customer
@app.route('/login/customer', methods=['POST'])
def login_customer():

    auth = request.get_json()

    if not auth or not auth["email"] or not auth["password"]:
        return jsonify({"success": "0",
                        "message": "Email or password cannot be empty"})

    user = Customer.query.filter_by(email=auth["email"].lower()).first()

    if not user:
        return jsonify({"success": "0", "message": "Customer not present"})

    if check_password_hash(user.password, auth["password"]):
        token = jwt.encode(
            {'customer_id': user.customer_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)},
            app.config['SECRET_KEY'])

        if "registration_id" in auth:
            user.device_id = auth["registration_id"]

            db.session.commit()

            return jsonify({"success": "1", "message": "Login Successful!",
                            "token": token.decode('UTF-8'),
                            "name": user.name,
                            "id": "updated"})

        return jsonify({"success": "1", "message": "Login Successful!",
                        "token": token.decode('UTF-8'),
                        "name": user.name})

    return jsonify({"success": "0", "message": "Could not verify"})


# get product by product id
@app.route('/product/item', methods=['GET'])
def show_product_item():

    pr_id = request.args.get('product_id')

    product = Products.query.filter_by(product_id=pr_id).first()

    rate = []
    output_data = {}
    output_data["product_id"] = product.product_id
    output_data["category"] = product.category_name
    output_data["product_name"] = product.product_name
    output_data["description"] = product.description
    output_data["prof_img"] = url_for('static',
                                      filename='images/product_prof_pic/'+product.prof_img)
    output_data["price"] = str(product.price)
    output_data["discounted_price"] = str(product.discount)
    output_data["offer"] = str(product.offer)
    ratings = Productratings.query\
        .filter_by(product=product).all()
    if ratings:
        for b in ratings:
            rate.append(b.rating)
            output_data["ratings"] = str((sum(rate))/len(rate))
    else:
        output_data["ratings"] = "0"

    return jsonify({"success": "1", "Product": output_data})


# get the citites
@app.route('/city', methods=['GET'])
def get_city():

    ven = Cityandcharge.query.all()
    cities = []

    if ven:
        for item in ven:
            if item.city not in cities:
                cities.append(item.city)

        return jsonify({"success": "1", "cities": cities})
    else:
        return jsonify({"success": "0", "message": "No Vendor yet"})


# get the delivery charge of city
@app.route('/city/charge', methods=['GET'])
def get_charge_city():
    if request.args:
        city = request.args.get('city')
        item = Cityandcharge.query.filter_by(city=city).first()

        return jsonify({"success": "1", "charge": item.delivery_charge})

    return jsonify({"success": "0", "message": 'data sent not correct format'})


# get category
@app.route('/category', methods=['GET'])
def get_category():

    if request.args:
        city = request.args.get('city')

        ven = Vendor.query.filter_by(city=city).all()

        categories = []

        if ven:
            for vendor in ven:
                products = Vendor_products.query\
                    .filter_by(vendor=vendor).all()

                for item in products:
                    print(item)
                    if item.category not in categories:
                        categories.append(item.category)
        else:
            return jsonify({"success": "0", "message": "No Vendor in Area"})

        output = []

        for i in categories:
            category = Category.query.filter_by(name=i).first()

            output_data = {}
            output_data["name"] = category.name
            output_data["prof_img"] = url_for('static',
                                              filename='images/category_prof_pic/'+category.prof_img)
            output.append(output_data)

        return jsonify({"success": "1", "All_Category": output})
    return jsonify({"success": "0", "message": "No Category"})


# get products of same category
@app.route('/category/items', methods=['GET'])
def get_category_items():

    if request.args:

        data = request.args

        ven = Vendor.query.filter_by(city=data["city"]).all()

        categories = []
        products = []
        available_products = []
        finished_products = []

        if ven:
            for vendor in ven:
                vendor_products = Vendor_products.query\
                    .filter_by(vendor=vendor).all()

                for item in vendor_products:
                    if item.category not in categories:
                        categories.append(item.category)
                    if item.available_status is False:
                        if item.product_id not in available_products and item.product_id not in products:
                            available_products.append(item.product_id)
                            products.append(item.product_id)
                    elif item.available_status is True:
                        if item.product_id not in finished_products and item.product_id not in products:
                            finished_products.append(item.product_id)
                            products.append(item.product_id)

        else:
            return jsonify({"success": "0", "message": "No Vendor in Area"})

        if data["category_name"] == "all":

            output = []

            for i in products:
                items = Products.query.filter_by(product_id=i).first()
                output_data = {}
                rate = []
                output_data["product_id"] = items.product_id
                output_data["category"] = items.category_name
                output_data["product_name"] = items.product_name
                output_data["description"] = items.description
                output_data["prof_img"] = url_for('static',
                                                  filename='images/product_prof_pic/'+items.prof_img)
                output_data["price"] = str(items.price)
                output_data["discounted_price"] = str(items.discount)
                output_data["offer"] = str(items.offer)
                ratings = Productratings.query\
                    .filter_by(product=items).all()
                if ratings:
                    for b in ratings:
                        rate.append(b.rating)
                    output_data["ratings"] = str((sum(rate))/len(rate))
                else:
                    output_data["ratings"] = "0"
                if i in available_products:
                    output_data["available"] = True
                elif i in finished_products:
                    output_data["available"] = False
                output.append(output_data)

            return jsonify({"success": "1",
                            "Products": output})

        elif data["category_name"] == "offer":
            output = []

            for i in products:
                items = Products.query.filter_by(product_id=i).first()
                if items.offer != 0:
                    output_data = {}
                    rate = []
                    output_data["product_id"] = items.product_id
                    output_data["category"] = items.category_name
                    output_data["product_name"] = items.product_name
                    output_data["description"] = items.description
                    output_data["prof_img"] = url_for('static',
                                                      filename='images/product_prof_pic/'+items.prof_img)
                    output_data["price"] = str(items.price)
                    output_data["discounted_price"] = str(items.discount)
                    output_data["offer"] = str(items.offer)
                    ratings = Productratings.query\
                        .filter_by(product=items).all()
                    if ratings:
                        for b in ratings:
                            rate.append(b.rating)
                        output_data["ratings"] = str((sum(rate))/len(rate))
                    else:
                        output_data["ratings"] = "0"
                    if i in available_products:
                        output_data["available"] = True
                    elif i in finished_products:
                        output_data["available"] = False
                    output.append(output_data)
                else:
                    continue

            return jsonify({"success": "1",
                            "Products": output})

        else:
            output = []

            for i in products:
                items = Products.query.filter_by(product_id=i).first()
                if items.category_name == data["category_name"]:
                    output_data = {}
                    rate = []
                    output_data["product_id"] = items.product_id
                    output_data["category"] = items.category_name
                    output_data["product_name"] = items.product_name
                    output_data["description"] = items.description
                    output_data["prof_img"] = url_for('static',
                                                      filename='images/product_prof_pic/'+items.prof_img)
                    output_data["price"] = str(items.price)
                    output_data["discounted_price"] = str(items.discount)
                    ratings = Productratings.query\
                        .filter_by(product=items).all()
                    if ratings:
                        for b in ratings:
                            rate.append(b.rating)
                        output_data["ratings"] = str((sum(rate))/len(rate))
                    else:
                        output_data["ratings"] = "0"
                    if i in available_products:
                        output_data["available"] = True
                    elif i in finished_products:
                        output_data["available"] = False
                    output.append(output_data)
                else:
                    continue

            return jsonify({"success": "1",
                            "Products": output})

    return jsonify({"success": "0", "message": "data sent not correct format"})


# get all the vendors available
@app.route('/all_vendor', methods=['GET'])
def show_vendor():

    allVendors = Vendor.query.all()

    output = []

    for vendor in allVendors:
        output_data = {}
        output_data["vendor_id"] = vendor.vendor_id
        output_data["email"] = vendor.email
        output_data["name"] = vendor.name
        output_data["contact"] = str(vendor.contact)
        output_data["store_name"] = vendor.store_name
        output_data["address"] = vendor.address
        output_data["prof_img"] = url_for('static',
                                          filename='images/vendor_prof_pic/'+vendor.prof_img)
        output.append(output_data)

    return jsonify({"success": "1", "All_Vendors": output})


# send all the promotional codes
@app.route('/promos', methods=['GET'])
def send_promo_code():
    promo = Promotionalcodes.query.all()
    if promo:
        output = []

        for i in promo:
            output_data = {}
            output_data["code"] = i.code
            output_data["discount"] = i.discount
            output.append(output_data)

        return jsonify({"success": "1", "promos": output})

    return jsonify({"success": "0", "message": "No promo Code till now"})


# send all the banner images
@app.route('/banner/images', methods=['GET'])
def send_banner_images():
    images = Bannerimages.query.get(1)

    if not images:
        return jsonify({"success": "0", "message": "No Banner Images"})

    output = []
    image_1 = url_for('static',
                      filename='images/banner_pics/'+images.image_1)
    image_2 = url_for('static',
                      filename='images/banner_pics/'+images.image_2)
    image_3 = url_for('static',
                      filename='images/banner_pics/'+images.image_3)
    image_4 = url_for('static',
                      filename='images/banner_pics/'+images.image_4)
    image_5 = url_for('static',
                      filename='images/banner_pics/'+images.image_5)

    output.append(image_1)
    output.append(image_2)
    output.append(image_3)
    output.append(image_4)
    output.append(image_5)

    return jsonify({"success": "1", "images": output})
