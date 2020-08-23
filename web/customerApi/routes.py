import string
import random
from flask import Blueprint, request, jsonify, url_for
from web import db
from web.models import Customer, Products, Cart, Ongoing_order,\
    Ongoing_order_products, Prev_order, Prev_order_products,\
    Vendor_rating, Favourites, Feedback, About, Privacypolicy,\
    Faq, Promotionalcodes, New_order, New_order_products, Vendor,\
    Vendor_products, Complaints, Productratings
from web.utils import login_required, select_vendor, send_push_vendor,\
    find_coord, send_push_customer
import uuid
from werkzeug.security import generate_password_hash


customer = Blueprint('Customer', __name__)


# registration for the customer
@customer.route('/create', methods=['POST'])
def create_customer():
    if request.is_json:
        data = request.get_json()

        cust = Customer.query.filter_by(email=data["email"].lower()).first()

        if cust:
            return jsonify({"success": "0",
                            "message": "Customer Already exist"})

        hashed_password = generate_password_hash(data["password"],
                                                 method='sha256')
        customer_id = str(uuid.uuid4())

        address = str(data["landmark"])+", "+str(data["locality"])+", "+str(data["city"])+", "+str(data["state"])+" "+str(data["pincode"])

        arr = find_coord(address)

        if data["contact_two"] == "":

            new_customer = Customer(customer_id=customer_id,
                                    email=data["email"].lower(),
                                    password=hashed_password,
                                    name=data["name"],
                                    contact_one=data["contact_one"],
                                    const_house_no=data["houseNo"],
                                    const_landmark=data["landmark"].lower(),
                                    const_locality=data["locality"].lower(),
                                    const_city=data["city"].lower(),
                                    const_state=data["state"].lower(),
                                    const_pincode=data["pincode"],
                                    delivery_house_no=data["houseNo"].lower(),
                                    delivery_landmark=data["landmark"].lower(),
                                    delivery_locality=data["locality"].lower(),
                                    delivery_city=data["city"].lower(),
                                    delivery_state=data["state"].lower(),
                                    delivery_pincode=data["pincode"],
                                    latitude=arr[0],
                                    longitude=arr[1])
        else:
            new_customer = Customer(customer_id=customer_id,
                                    email=data["email"].lower(),
                                    password=hashed_password,
                                    name=data["name"],
                                    contact_one=data["contact_one"],
                                    contact_two=data["contact_two"],
                                    const_house_no=data["houseNo"],
                                    const_landmark=data["landmark"].lower(),
                                    const_locality=data["locality"].lower(),
                                    const_city=data["city"].lower(),
                                    const_state=data["state"].lower(),
                                    const_pincode=data["pincode"],
                                    delivery_house_no=data["houseNo"],
                                    delivery_landmark=data["landmark"].lower(),
                                    delivery_locality=data["locality"].lower(),
                                    delivery_city=data["city"].lower(),
                                    delivery_state=data["state"].lower(),
                                    delivery_pincode=data["pincode"],
                                    latitude=arr[0],
                                    longitude=arr[1])

        try:
            db.session.add(new_customer)
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "Customer registration successfull!!"})
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"success": "0",
                            "message": "Customer registration failed"})

    return jsonify({"success": "0", "message": "data sent not correct format"})


# show profile of the customer
@customer.route('/profile', methods=['GET'])
@login_required
def get_profile(current_user):

    cust = Customer.query.filter_by(customer_id=current_user.customer_id)\
        .first()

    customer = {}
    customer["email"] = cust.email
    customer["name"] = cust.name
    customer["contact_one"] = cust.contact_one
    customer["contact_two"] = cust.contact_two
    customer["houseNo"] = cust.const_house_no
    customer["landmark"] = cust.const_landmark
    customer["locality"] = cust.const_locality
    customer["city"] = cust.const_city
    customer["state"] = cust.const_state
    customer["pincode"] = str(cust.const_pincode)
    customer["delivery_houseNo"] = cust.delivery_house_no
    customer["delivery_landmark"] = cust.delivery_landmark
    customer["delivery_locality"] = cust.delivery_locality
    customer["delivery_city"] = cust.delivery_city
    customer["delivery_state"] = cust.delivery_state
    customer["delivery_pincode"] = str(cust.delivery_pincode)

    return jsonify({"success": "1", "customer_detail": customer})


# update profile of the customer
@customer.route('/profile/update', methods=['PUT'])
@login_required
def update_profile(current_user):
    if request.is_json:
        data = request.get_json()

        cust = Customer.query.filter_by(customer_id=current_user.customer_id)\
            .first()
        if len(data) == 1:
            try:
                if "name" in data:
                    cust.name = data["name"]
                elif "email" in data:
                    cust.email = data["email"].lower()
                elif "contact_one" in data:
                    cust.contact_one = data["contact_one"]
                elif "contact_two" in data:
                    cust.contact_two = data["contact_two"]
                else:
                    return jsonify({"success": "0",
                                    "message": "No key found"})
                db.session.commit()

                return jsonify({"success": "1",
                                "message": "Record updated successfully!!"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Record update failed"})

        else:
            try:
                if "address" in data:
                    if data["address"] == "constant":
                        cust.const_house_no = data["houseNo"]
                        cust.const_landmark = data["landmark"].lower()
                        cust.const_locality = data["locality"].lower()
                        cust.const_city = data["city"].lower()
                        cust.const_state = data["state"].lower()
                        cust.const_pincode = int(data["pincode"])

                        address = str(data["landmark"])+", "+str(data["locality"])+", "+str(data["city"])+", "+str(data["state"])+" "+str(data["pincode"])

                        arr = find_coord(address)

                        cust.latitude = arr[0]
                        cust.longitude = arr[1]
                    elif data["address"] == "delivery":
                        cust.delivery_house_no = data["houseNo"]
                        cust.delivery_landmark = data["landmark"].lower()
                        cust.delivery_locality = data["locality"].lower()
                        cust.delivery_city = data["city"].lower()
                        cust.const_state = data["state"].lower()
                        cust.delivery_pincode = int(data["pincode"])
                else:
                    return jsonify({"success": "0",
                                    "message": "No key found"})
                db.session.commit()

                return jsonify({"success": "1",
                                "message": "Record updated successfully!!"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Record update failed"})

    return jsonify({"success": "0", "message": "data sent not correct format"})


# get the cart details of the customer
@customer.route('/order/cart', methods=['GET'])
@login_required
def order_cart(current_user):
    cust = Customer.query.filter_by(customer_id=current_user.customer_id)\
        .first()

    items = Cart.query.filter_by(customer_cart=cust).all()
    if items:
        output = []
        for item in items:
            product = Products.query.filter_by(product_id=item.product_id)\
                .first()
            product_data = {}
            product_data["product_id"] = product.product_id
            product_data["category"] = product.category_name
            product_data["product_name"] = product.product_name
            product_data["img"] = url_for('static',
                                          filename='images/product_prof_pic/' + product.prof_img)
            product_data["price"] = product.price
            product_data["discounted_price"] = product.discount
            product_data["offer"] = product.offer
            product_data["quantity"] = item.quantity
            output.append(product_data)

        return jsonify({"success": "1", "cart_items": output})
    return jsonify({"success": "0", "message": "Nothing in Cart"})


# add items to the cart
@customer.route('/order/cart/add', methods=['POST'])
@login_required
def order_cart_add(current_user):
    if request.is_json:
        data = request.get_json()

        pr = Cart.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=data["product_id"])\
            .first()

        if pr:
            return jsonify({"success": "0", "message": "Item already in cart"})

        new = Cart(product_id=data["product_id"],
                   quantity=data["quantity"],
                   customer_details=current_user.customer_id)

        try:
            db.session.add(new)
            db.session.commit()

            return jsonify({"success": "1", "message": "item added to cart"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "Item not added to cart"})

    return jsonify({"succes": "0", "message": "data sent not correct format"})


# remove item from cart
@customer.route('/order/cart/remove', methods=['DELETE'])
@login_required
def order_cart_delete(current_user):
    if request.args:
        product_id = request.args.get('product_id')

        item = Cart.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=product_id)\
            .first()

        try:
            db.session.delete(item)
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "item deleted from cart"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "item not deleted"})

    return jsonify({"succes": "0", "message": "data sent not correct format"})


# increase quantity of the cart item
@customer.route('/order/cart/increase', methods=['PUT'])
@login_required
def order_cart_increase(current_user):
    if request.args:
        pr_id = request.args.get('product_id')

        item = Cart.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=pr_id).first()

        try:
            item.quantity = item.quantity + 1
            db.session.commit()

            return jsonify({"success": "1", "quantity": item.quantity})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "quantity not increased"})
    return jsonify({"succes": "0", "message": "data sent not correct format"})


# decrease quantity of the cart item
@customer.route('/order/cart/decrease', methods=['PUT'])
@login_required
def order_cart_deacrease(current_user):
    if request.args:
        pr_id = request.args.get('product_id')

        item = Cart.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=pr_id).first()

        try:
            if item.quantity > 0:
                item.quantity = item.quantity - 1
                db.session.commit()

                return jsonify({"success": "1", "quantity": item.quantity})
            return jsonify({"success": "1", "quantity": item.quantity})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "quantity not deacreased"})
    return jsonify({"succes": "0", "message": "data sent not correct format"})


# send order to vendor/place order by the customer
@customer.route('/order/new', methods=['POST'])
@login_required
def order_new(current_user):
    if request.is_json:

        data = request.get_json()

        near_vendor = select_vendor(current_user.latitude,
                                    current_user.longitude,
                                    current_user.const_city)

        output = []
        amt = []

        for i in range(0, len(data)):
            if i == 0:
                order_data = {}
                order_data["total_amount"] = data[i]["total_amount"]
                order_data["delivery_method"] = data[i]["delivery_method"]
            else:
                product_data = {}
                product_data["product_id"] = data[i]["product_id"]
                product_data["quantity"] = int(data[i]["quantity"])
                product_data["total_price"] = int(data[i]["total_price"])
                amt.append(int(data[i]["total_price"]))
                output.append(product_data)

        alphabet = string.ascii_letters + string.digits
        order_id = ''.join(random.choice(alphabet) for i in range(7))

        if len(near_vendor) == 1:
            vendor_id = near_vendor[0]["vendor_id"]
        else:
            for z in range(len(near_vendor)):
                ven = Vendor.query\
                    .filter_by(vendor_id=near_vendor[z]["vendor_id"]).first()

                product_list = []

                products = Vendor_products.query.filter_by(vendor=ven).all()

                for a in products:
                    if a.product_id not in product_list:
                        product_list.append(a.product_id)

                if output[0]["product_id"] not in product_list:
                    continue
                else:
                    item = Vendor_products.query\
                        .filter_by(vendor_details=near_vendor[z]["vendor_id"],
                                   product_id=output[0]["product_id"]).first()
                    if item.available_status is True:
                        continue
                    else:
                        vendor_id = near_vendor[z]["vendor_id"]
                        break

        address = str(current_user.delivery_house_no)+", "+str(current_user.delivery_landmark)+", "+str(current_user.delivery_locality)+", "+str(current_user.delivery_city)+", "+str(current_user.delivery_state)+" "+str(current_user.delivery_pincode)

        if order_data["delivery_method"] == "default":

            new = New_order(order_id=order_id,
                            customer_id=current_user.customer_id,
                            delivery_address=address,
                            bill=int(sum(amt)),
                            total_bill=round(float(order_data["total_amount"])),
                            vendor_details=vendor_id)

        else:
            new = New_order(order_id=order_id,
                            customer_id=current_user.customer_id,
                            delivery_address=address,
                            delivery_method=order_data["delivery_method"],
                            bill=int(sum(amt)),
                            total_bill=int(order_data["total_amount"]),
                            vendor_details=vendor_id)

        db.session.add(new)

        for y in range(0, len(output)):
            order_products = New_order_products(product_id=output[y]["product_id"],
                                                quantity=output[y]["quantity"],
                                                total_price=output[y]["total_price"],
                                                order=order_id)

            prev = Cart.query\
                .filter_by(customer_details=current_user.customer_id,
                           product_id=output[y]["product_id"]).first()

            db.session.add(order_products)
            db.session.delete(prev)

        try:
            db.session.commit()

            ven = Vendor.query\
                .filter_by(vendor_id=vendor_id).first()

            customer_message_title = "Order Placed"
            customer_message_body = f"Your order id: { order_id }, has been placed and is pending approval from your nearest vendor"

            vendor_message_title = "Order Received"
            vendor_message_body = f"order id: { order_id } received,Please open new orders in app to view details"

            customer_res = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              current_user.device_id)

            vendor_res = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          ven.device_id)

            return jsonify({"success": "1", "Order_Added": order_id,
                            "cust_noti": customer_res,
                            "ven_noti": vendor_res})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "Order_Added": "failed"})

    return jsonify({"succes": "0",
                    "message": "data sent not correct format"})


# get the new orders of the customer
@customer.route('/order/new', methods=['GET'])
@login_required
def order_new_show(current_user):
    new_orders = New_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    output = []
    if new_orders:
        for order in new_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["delivery_address"] = order.delivery_address
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_date"] = order.order_date
            output_data["vendor_id"] = order.vendor_details
            products = New_order_products.query\
                .filter_by(new_order=order).all()
            for product in products:
                product_list = {}
                item = Products.query\
                    .filter_by(product_id=product.product_id).first()
                product_list["product_id"] = product.product_id
                product_list["product_name"] = item.product_name
                product_list["prof_img"] = url_for('static',
                                                   filename='images/product_prof_pic/'+item.prof_img)
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                products_data.append(product_list)
            output_data["products"] = products_data
            output.append(output_data)

        return jsonify({"success": "1", "new_Orders": output})

    return jsonify({"success": "0", "message": "No ongoing Orders"})


# get the ongoing orders of the customer
@customer.route('/order/ongoing', methods=['GET'])
@login_required
def order_ongoing(current_user):
    ongoing_orders = Ongoing_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    output = []
    if ongoing_orders:
        for order in ongoing_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_approve_date"] = order.order_approve_date
            output_data["pickup_status"] = order.pickup_status
            output_data["vendor_id"] = order.vendor_details
            products = Ongoing_order_products.query\
                .filter_by(ongoing_order=order).all()
            for product in products:
                product_list = {}
                item = Products.query\
                    .filter_by(product_id=product.product_id).first()
                product_list["product_id"] = product.product_id
                product_list["product_name"] = item.product_name
                product_list["prof_img"] = url_for('static',
                                                   filename='images/product_prof_pic/'+item.prof_img)
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                products_data.append(product_list)
            output_data["products"] = products_data
            output.append(output_data)

        return jsonify({"success": "1", "Ongoing_Orders": output})

    return jsonify({"success": "0", "message": "No ongoing Orders"})


# get the previous orders of the customer
@customer.route('/order/previous', methods=['GET'])
@login_required
def order_previous(current_user):
    prev_orders = Prev_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    output = []
    if prev_orders:

        for order in prev_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["complete_date"] = order.complete_date
            output_data["vendor_id"] = order.vendor_details
            ratings = Vendor_rating.query\
                .filter_by(customer_id=current_user.customer_id,
                           vendor_details=order.vendor_details).first()
            if ratings:
                output_data["vendor_rating"] = ratings.rating
            else:
                output_data["vendor_rating"] = "0"
            products = Prev_order_products.query\
                .filter_by(complete_order=order).all()
            for product in products:
                product_list = {}
                item = Products.query\
                    .filter_by(product_id=product.product_id).first()
                p_rating = Productratings.query\
                    .filter_by(customer_id=current_user.customer_id,
                               product_details=product.product_id).first()
                if p_rating:
                    product_list["rating"] = str(p_rating.rating)
                else:
                    product_list["rating"] = "0"
                product_list["product_id"] = product.product_id
                product_list["product_name"] = item.product_name
                product_list["prof_img"] = url_for('static',
                                                   filename='images/product_prof_pic/'+item.prof_img)
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                products_data.append(product_list)
            output_data["products"] = products_data
            output.append(output_data)

        return jsonify({"success": "1", "Previous_Orders": output})

    return jsonify({"success": "0", "message": "No previous Orders"})


# submit complain from customer
@customer.route('/complain', methods=['POST'])
@login_required
def complains_new(current_user):
    if request.is_json:
        data = request.get_json()

        alphabet = string.ascii_letters + string.digits
        complain_id = ''.join(random.choice(alphabet) for i in range(7))

        new = Complaints(complain_id=complain_id,
                         order_id=data["order_id"],
                         customer_id=current_user.customer_id,
                         title=data["title"],
                         description=data["description"],
                         vendor_details=data["vendor_id"])

        try:
            db.session.add(new)
            db.session.commit()

            return jsonify({"success": "1", "message": "comlain submmitted",
                            "complain_id": complain_id})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "error occured"})

    return jsonify({"success": "0",
                    "message": "data format sent is not correct"})


# submit feedback from customer
@customer.route('/feedback', methods=['POST'])
@login_required
def feedback_new(current_user):
    if request.is_json:
        data = request.get_json()

        feed = Feedback(customer_id=current_user.customer_id,
                        description=data["description"])

        try:
            db.session.add(feed)
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "Feedback submitted Successfully!!"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "Feedback not submiited"})
    return jsonify({"success": "0", "message": "data sent not correct format"})


# favourites of the customer
@customer.route('/favourites', methods=['GET'])
@login_required
def favourites_get(current_user):
    cust = Customer.query.filter_by(customer_id=current_user.customer_id)\
        .first()

    items = Favourites.query.filter_by(customer_fav=cust).all()
    if items:
        output = []
        for item in items:
            product = Products.query.filter_by(product_id=item.product_id)\
                .first()
            product_data = {}
            product_data["product_id"] = product.product_id
            product_data["category"] = product.category_name
            product_data["product_name"] = product.product_name
            product_data["description"] = product.description
            product_data["prof_img"] = url_for('static',
                                               filename='images/product_prof_pic/' + product.prof_img)
            product_data["price"] = str(product.price)
            product_data["discounted_price"] = str(product.discount)
            output.append(product_data)

        return jsonify({"success": "1", "fav_items": output})
    return jsonify({"success": "0", "message": "Nothing in favourites"})


# add to favourites of the customer
@customer.route('/favourites/add', methods=['POST'])
@login_required
def favourites_add(current_user):
    if request.is_json:
        data = request.get_json()
        product_id = data["product_id"]

        pr = Favourites.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=product_id).first()
        if pr:
            return jsonify({"success": "0",
                            "message": "item already in favourites"})

        new = Favourites(product_id=product_id,
                         customer_details=current_user.customer_id)
        try:
            db.session.add(new)
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "item added to favourites"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "item not added"})

    return jsonify({"succes": "0", "message": "data sent not correct format"})


# remove item from favourites
@customer.route('/favourites/remove', methods=['DELETE'])
@login_required
def favourites_remove(current_user):
    if request.args:
        product_id = request.args.get('product_id')
        new = Favourites.query\
            .filter_by(product_id=product_id,
                       customer_details=current_user.customer_id)\
            .first()

        try:
            db.session.delete(new)
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "item removed favourites"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "item not removed"})

    return jsonify({"succes": "0", "message": "data sent not correct format"})


# get the about section of the app
@customer.route('/about', methods=['GET'])
def about_get():
    about = About.query.get(1)
    if about:
        return jsonify({"success": "1", "message": about.description})
    return jsonify({"success": "0", "message": "No about section found"})


# get the privacy policy of the app
@customer.route('/privacy_policy', methods=['GET'])
def policy_get():
    privacy = Privacypolicy.query.all()
    output = []
    for i in privacy:
        output_data = {}
        output_data["title"] = i.title
        output_data["description"] = i.description
        output.append(output_data)

    return jsonify({"success": "1",
                    "message": output})


# get the Faq of the app
@customer.route('/faq', methods=['GET'])
def faq_get():
    questions = Faq.query.all()
    output = []
    for i in questions:
        output_data = {}
        output_data["title"] = i.title
        output_data["description"] = i.description
        output.append(output_data)

    return jsonify({"success": "1",
                    "message": output})


# submit rating for the vendor
@customer.route('/ratings/new', methods=['POST'])
@login_required
def ratings_new(current_user):
    if request.is_json:
        data = request.get_json()

        rate = Vendor_rating.query\
            .filter_by(customer_id=current_user.customer_id,
                       vendor_details=data["vendor_id"]).first()
        if rate:
            rate.rating = int(data["rating"])
            try:
                db.session.commit()

                return jsonify({"success": "1", "message": "Ratings saved"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Ratings cannot be saved"})
        else:

            ratings = Vendor_rating(rating=int(data["rating"]),
                                    customer_id=current_user.customer_id,
                                    vendor_details=data["vendor_id"])

            try:
                db.session.add(ratings)
                db.session.commit()

                return jsonify({"success": "1", "message": "Ratings saved"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Ratings cannot be saved"})

    return jsonify({"succes": "0",
                    "message": "data sent not correct format"})


# submit rating for the product
@customer.route('/ratings/products', methods=['POST'])
@login_required
def ratings_products(current_user):
    if request.is_json:
        data = request.get_json()

        rate = Productratings.query\
            .filter_by(customer_id=current_user.customer_id,
                       product_details=data["product_id"]).first()
        if rate:
            rate.rating = int(data["rating"])
            try:
                db.session.commit()

                return jsonify({"success": "1", "message": "Ratings saved"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Ratings cannot be saved"})
        else:
            ratings = Productratings(rating=int(data["rating"]),
                                     customer_id=current_user.customer_id,
                                     product_details=data["product_id"])

            try:
                db.session.add(ratings)
                db.session.commit()

                return jsonify({"success": "1", "message": "Ratings saved"})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0",
                                "message": "Ratings cannot be saved"})

    return jsonify({"succes": "0",
                    "message": "data sent not correct format"})


# check the promo code for the cart
@customer.route('/promo/check', methods=['GET'])
@login_required
def check_promo_code(current_user):
    if request.args:
        code = request.args.get('code')
        promo = Promotionalcodes.query.filter_by(code=code).first()
        if promo:
            return jsonify({"success": "1", "discount": promo.discount})

        return jsonify({"success": "0", "message": "Promo Code not valid"})

    return jsonify({"success": "0", "message": "data sent not correct format"})


# cancel the order
@customer.route('/order/ongoing/cancel', methods=['DELETE'])
@login_required
def cancel_order(current_user):
    if request.args:
        data = request.args.get('order_id')

        new_orders = Ongoing_order.query.filter_by(order_id=data)\
            .first()

        new_orders_one = New_order.query.filter_by(order_id=data)\
            .first()

        try:

            if new_orders:
                ven = Vendor.query\
                    .filter_by(vendor_id=new_orders.vendor_details)\
                    .first()
            elif new_orders_one:
                ven = Vendor.query\
                    .filter_by(vendor_id=new_orders_one.vendor_details)\
                    .first()

            if new_orders:
                customer_message_title = "Order Declined"
                customer_message_body = f"Your order id: { new_orders.order_id }, has been cancelled by you!!"

                vendor_message_title = "Order Declined"
                vendor_message_body = f"Order id: { new_orders.order_id }, has been cancelled by the customer!!"

            elif new_orders_one:
                customer_message_title = "Order Declined"
                customer_message_body = f"Your order id: { new_orders_one.order_id }, has been cancelled by you!!"

                vendor_message_title = "Order Declined"
                vendor_message_body = f"Order id: { new_orders_one.order_id }, has been cancelled by the customer!!"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              current_user.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          ven.device_id)

            if new_orders:
                db.session.delete(new_orders)
            elif new_orders_one:
                db.session.delete(new_orders_one)

            db.session.commit()

            return jsonify({"success": "1", "message": "Order Cancelled",
                            "cust_noti": res_customer, "ven_noti": res_vendor})

        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "could not be cancelled"})

    return jsonify({"success": "0", "message": "data sent not correct format"})
