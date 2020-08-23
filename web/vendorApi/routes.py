import random
import string
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for
from web import db
from web.models import Vendor, Vendor_products, Complaints,\
    New_order, New_order_products, Ongoing_order, Ongoing_order_products,\
    Prev_order, Prev_order_products, Vendor_rating, Deliveryboy, Customer,\
    Deliveryboy, Products
from web.utils import login_required, save_vendor_pic,\
    save_deliveryBoy_aadharpic, send_push_customer, find_coord,\
    send_push_vendor, send_push_driver
import uuid
from werkzeug.security import generate_password_hash

vendor = Blueprint('Vendor', __name__)


# create a new vendor
@vendor.route('/create', methods=['POST'])
def create_vendor():

    data = request.get_json()

    ven = Vendor.query.filter_by(email=data["email"].lower()).first()

    if ven:
        return jsonify({"success": "0", "message": "Vendor already exist"})

    hashed_password = generate_password_hash(data["password"], method='sha256')

    vendor_id = str(uuid.uuid4())

    address = str(data["landmark"])+", "+str(data["locality"])+", "+str(data["city"])+", "+str(data["state"])+" "+str(data["pincode"])

    arr = find_coord(address)

    city_name = data["city"]

    new_user = Vendor(vendor_id=vendor_id,
                      email=data["email"].lower(),
                      password=hashed_password,
                      name=data["name"],
                      contact=data["contact"],
                      store_name=data["store_name"],
                      house_no=data["houseNo"],
                      landmark=data["landmark"].lower(),
                      locality=data["locality"].lower(),
                      city=city_name.lower(),
                      state=data["state"].lower(),
                      pincode=int(data["pincode"]),
                      latitude=arr[0],
                      longitude=arr[1]
                      )

    db.session.add(new_user)

    new_settings = Delivery_options(vendor_details=vendor_id)

    db.session.add(new_settings)
    db.session.commit()

    return jsonify({"success": "1", "message": "New Vendor created"})


# vendor profile
@vendor.route('/profile', methods=['GET'])
@login_required
def show_profile(current_user):

    output_data = {}
    output_data["vendor_id"] = current_user.vendor_id
    output_data["email"] = current_user.email
    output_data["name"] = current_user.name
    output_data["contact"] = current_user.contact
    output_data["store_name"] = current_user.store_name
    output_data["houseNo"] = current_user.house_no
    output_data["landmark"] = current_user.landmark
    output_data["locality"] = current_user.locality
    output_data["city"] = current_user.city
    output_data["state"] = current_user.state
    output_data["pincode"] = str(current_user.pincode)
    output_data["prof_img"] = url_for('static',
                                      filename='images/vendor_prof_pic/'+current_user.prof_img)

    return jsonify({"success": "1", "vendor": output_data})


# update vendor details
@vendor.route('/update', methods=['PUT'])
@login_required
def update_vendor(current_user):
    data = request.get_json()

    ven = Vendor.query\
        .filter_by(vendor_id=current_user.vendor_id).first()

    ven.email = data["email"].lower()
    ven.name = data["name"]
    ven.contact = data["contact"]
    ven.store_name = data["store_name"]
    ven.house_no = data["houseNo"]
    ven.landmark = data["landmark"].lower()
    ven.locality = data["locality"].lower()
    ven.city = data["city"].lower()
    ven.state = data["state"].lower()
    ven.pincode = int(data["pincode"])

    address = str(data["landmark"])+", "+str(data["locality"])+", "+str(data["city"])+", "+str(data["state"])+" "+str(data["pincode"])

    arr = find_coord(address)

    ven.latitude = arr[0]
    ven.longitude = arr[1]

    db.session.commit()

    return jsonify({"success": "1", "message": "Vendor Details updated"})


# upload vendor profile pic
@vendor.route('/prof_pic/upload', methods=['POST'])
@login_required
def upload_vendor_img(current_user):

    file_name = request.files['file']
    file_t = save_vendor_pic(file_name)
    if current_user.vendor_id:
        ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
            .first()
        ven.prof_img = file_t

        db.session.commit()

        return jsonify({"success": "1", "message": "File saved successfully",
                        "file_name": file_t})
    return jsonify({"success": "0", "message": "not a vendor"})


# get all the products vendor got from admin
@vendor.route('/products', methods=['GET'])
@login_required
def show_products(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()

    products = Vendor_products.query.filter_by(vendor=ven).all()

    if products:

        output = []

        for product in products:
            output_data = {}
            output_data["product_id"] = product.product_id
            output_data["category"] = product.category
            output_data["product_name"] = product.product_name
            output_data["price"] = str(product.price)
            output_data["discount"] = str(product.discount)
            output_data["offer"] = str(product.offer)
            output_data["quantity_left"] = str(product.quantity_left)
            output_data["quantity_recieved"] = str(product.quantity_recieved)
            output_data["product_received_date"] = product\
                .product_received_date
            output_data["available"] = product.available_status
            output.append(output_data)

        return jsonify({"success": "1", "Vendor_Products": output})
    return jsonify({"success": "0",
                    "message": "No products received till now"})


# make products available/un-available
@vendor.route('/products/status/update', methods=['PUT'])
@login_required
def update_product_status(current_user):
    if request.args:
        data = request.args

    if data["status"] == "1":
        product = Vendor_products.query\
            .filter_by(vendor_details=current_user.vendor_id,
                       product_id=data["product_id"]).first()

        product.available_status = False

        try:
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "Product status available"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "error occured"})

    elif data["status"] == "0":
        product = Vendor_products.query\
            .filter_by(vendor_details=current_user.vendor_id,
                       product_id=data["product_id"]).first()

        product.available_status = True

        try:
            db.session.commit()

            return jsonify({"success": "1",
                            "message": "Product status unavailable"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "error occured"})


# get the complains sended to the vendor from the admin
@vendor.route('/complains', methods=['GET'])
@login_required
def vendor_complain(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()

    complains = Complaints.query.filter_by(vendor=ven).all()

    count = 0

    if complains:
        output = []

        for complain in complains:
            output_data = {}
            if complain.send_vendor_status is True:
                output_data["complain_id"] = complain.complain_id
                output_data["order_id"] = complain.order_id
                output_data["customer_id"] = complain.customer_id
                output_data["title"] = complain.title
                output_data["description"] = complain.description
                output_data["complain_date"] = complain.complain_date
                output_data["status"] = complain.status
                output.append(output_data)
                count = 1

    if count == 0:
        return jsonify({"success": "0", "message": "No Complains"})
    else:
        return jsonify({"success": "1", "Complains": output})


# accept/reject complain
@vendor.route('/complains/update', methods=['PUT'])
@login_required
def vendor_complain_update(current_user):

    data = request.args

    complain = Complaints.query\
        .filter_by(complain_id=data['complain_id'])\
        .first()

    if data['status'] == '1':
        complain.status = True
    elif data['status'] == '0':
        complain.status = False

    db.session.commit()

    return jsonify({"success": "1", "message": "complain status updated"})


# get the new orders of the vendor
@vendor.route('/order/new', methods=['GET'])
@login_required
def vendor_order_new(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = New_order.query.filter_by(vendor=ven).all()

    output = []
    if new_orders:

        for order in new_orders:
            output_data = {}
            products_data = []
            cust = Customer.query\
                .filter_by(customer_id=order.customer_id).first()
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["customer_name"] = cust.name
            output_data["delivery_address"] = order.delivery_address
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_date"] = order.order_date
            output_data["delivery_time"] = order.delivery_method
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

        return jsonify({"success": "1", "New_Orders": output})

    return jsonify({"success": "0", "message": "No New Orders"})


# accept/decline the new orders coming
@vendor.route('/order/new/update', methods=['POST'])
@login_required
def vendor_order_update(current_user):

    data = request.args

    new_orders = New_order.query\
        .filter_by(order_id=data['order_id'])\
        .first()

    if data['status'] == '1' and data["driver_id"] != '':
        new_orders.status = True
        curr_order = Ongoing_order(order_id=new_orders.order_id,
                                   customer_id=new_orders.customer_id,
                                   delivery_address=new_orders.delivery_address,
                                   delivery_boy_id=data["driver_id"],
                                   bill=new_orders.bill,
                                   total_bill=new_orders.total_bill,
                                   delivery_method=new_orders.delivery_method,
                                   vendor_details=new_orders.vendor_details)
        db.session.add(curr_order)
        products = New_order_products.query\
            .filter_by(new_order=new_orders).all()
        for product in products:
            order_products = Ongoing_order_products(product_id=product.product_id,
                                                    quantity=product.quantity,
                                                    total_price=str(product.total_price),
                                                    order=data['order_id'])
            db.session.add(order_products)

        try:
            db.session.commit()

            cust = Customer.query\
                .filter_by(customer_id=new_orders.customer_id).first()

            driver = Deliveryboy.query\
                .filter_by(driver_id=data["driver_id"]).first()

            customer_message_title = "Order Approved"
            customer_message_body = f"Your order id: { new_orders.order_id }, has been approved by the vendor and will be delivered to you shortly!"

            vendor_message_title = "Order Approved"
            vendor_message_body = f"Order id: { new_orders.order_id }, has been approved by you and assinged delivery boy id is: { data['driver_id'] }"

            driver_message_title = "Order Assinged"
            driver_message_body = f"Order id: { new_orders.order_id }, has been assinged to you for delivery"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              cust.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          current_user.device_id)

            res_driver = send_push_driver(driver_message_title,
                                          driver_message_body,
                                          driver.device_id)

            db.session.delete(new_orders)
            db.session.commit()

            return jsonify({"success": "1", "message": "Order Accepted",
                            "cust_noti": res_customer, "ven_noti": res_vendor,
                            "driv_noti": res_driver})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Some issue occured"})

    elif data['status'] == '0':
        new_orders.status = False

        new_orders = New_order.query.filter_by(order_id=data['order_id'])\
            .first()

        try:
            cust = Customer.query\
                .filter_by(customer_id=new_orders.customer_id).first()

            customer_message_title = "Order Declined"
            customer_message_body = f"Your order id: { new_orders.order_id }, has been declined by the vendor!!"

            vendor_message_title = "Order Declined"
            vendor_message_body = f"Order id: { new_orders.order_id }, has been declined!!"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              cust.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          current_user.device_id)

            db.session.delete(new_orders)
            db.session.commit()

            return jsonify({"success": "1", "message": "Order Declined",
                            "cust_noti": res_customer, "ven_noti": res_vendor})

        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Some issue occured"})

    return jsonify({"success": "0", "message": "Order Not Created"})


# update and accept the new orders
@vendor.route('/order/new/update/new', methods=['PUT'])
@login_required
def vendor_order_update_change(current_user):

    data = request.get_json()

    output = []

    for i in range(0, len(data)):
        if i == 0:
            order_data = {}
            order_data["order_id"] = data[i]["order_id"]
            order_data["delivery_boy_id"] = data[i]["driver_id"]
            order_data["bill"] = data[i]["bill"]
            order_data["total_bill"] = data[i]["total_bill"]
            order_data["status"] = data[i]["status"]
        else:
            product_data = {}
            product_data["product_id"] = data[i]["product_id"]
            product_data["quantity"] = int(data[i]["quantity"])
            product_data["total_price"] = int(data[i]["total_price"])
            output.append(product_data)

    new_orders = New_order.query\
        .filter_by(order_id=order_data["order_id"])\
        .first()

    if order_data["status"] == '1' and data["driver_id"] != '':

        new_orders.status = True
        curr_order = Ongoing_order(order_id=new_orders.order_id,
                                   customer_id=new_orders.customer_id,
                                   delivery_address=new_orders.delivery_address,
                                   delivery_boy_id=order_data["delivery_boy_id"],
                                   bill=int(order_data["bill"]),
                                   total_bill=int(order_data["total_bill"]),
                                   delivery_method=new_orders.delivery_method,
                                   vendor_details=new_orders.vendor_details)

        db.session.add(curr_order)
        for y in output:
            order_products = Ongoing_order_products(product_id=y["product_id"],
                                                    quantity=y["quantity"],
                                                    total_price=y["total_price"],
                                                    order=order_data["order_id"])

            db.session.add(order_products)

        try:
            db.session.commit()

            cust = Customer.query\
                .filter_by(customer_id=new_orders.customer_id).first()

            driver = Deliveryboy.query\
                .filter_by(driver_id=data["driver_id"]).first()

            customer_message_title = "Order Approved"
            customer_message_body = f"Your order id: { new_orders.order_id }, has been updated and approved by the vendor and the new total amount is { order_data['total_bill'] } and will be delivered to you shortly!"

            vendor_message_title = "Order Approved"
            vendor_message_body = f"Order id: { new_orders.order_id }, has been approved by you and assinged delivery boy id is: { data['driver_id'] }"

            driver_message_title = "Order Assinged"
            driver_message_body = f"Order id: { new_orders.order_id }, has been assinged to you for delivery"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              cust.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          current_user.device_id)

            res_driver = send_push_driver(driver_message_title,
                                          driver_message_body,
                                          driver.device_id)

            db.session.delete(new_orders)
            db.session.commit()

            return jsonify({"success": "1", "message": "Order Accepted",
                            "cust_noti": res_customer, "ven_noti": res_vendor,
                            "driv_noti": res_driver})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Some issue occured"})

    elif data["status"] == '0':
        new_orders.status = False

        try:
            cust = Customer.query\
                .filter_by(customer_id=new_orders.customer_id).first()

            customer_message_title = "Order Declined"
            customer_message_body = f"Your order id: { new_orders.order_id }, has been declined by the vendor!!"

            vendor_message_title = "Order Declined"
            vendor_message_body = f"Order id: { new_orders.order_id }, has been declined!!"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              cust.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          current_user.device_id)

            db.session.delete(new_orders)
            db.session.commit()

            return jsonify({"success": "1", "message": "Order Declined",
                            "cust_noti": res_customer, "ven_noti": res_vendor})

        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Some issue occured"})

    return jsonify({"success": "0", "message": "Order Not Updated"})


# get all the ongoing orders
@vendor.route('/order/ongoing', methods=['GET'])
@login_required
def vendor_order_ongoing(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Ongoing_order.query.filter_by(vendor=ven).all()

    output = []
    if new_orders:

        for order in new_orders:
            output_data = {}
            products_data = []
            cust = Customer.query\
                .filter_by(customer_id=order.customer_id).first()
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["customer_name"] = cust.name
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_approve_date"] = order.order_approve_date
            output_data["delivery_method"] = order.delivery_method
            output_data["pickup_status"] = order.pickup_status
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


# get all the previous orders
@vendor.route('/order/previous', methods=['GET'])
@login_required
def vendor_order_pervious(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    output = []
    if new_orders:

        for order in new_orders:
            output_data = {}
            products_data = []
            cust = Customer.query\
                .filter_by(customer_id=order.customer_id).first()
            output_data["order_id"] = order.order_id
            output_data["customer_id"] = order.customer_id
            output_data["customer_name"] = cust.name
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["bill"] = str(order.bill)
            output_data["total_bill"] = str(order.total_bill)
            output_data["complete_date"] = order.complete_date
            output_data["delivery_method"] = order.delivery_method
            products = Prev_order_products.query\
                .filter_by(complete_order=order).all()
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

        return jsonify({"success": "1", "Previous_Orders": output})

    return jsonify({"success": "0", "message": "No previous Orders"})


# get the sales deatils of the current day
@vendor.route('/sales/daily', methods=['GET'])
@login_required
def vendor_sales_daily(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    output = []

    for order in new_orders:
        if str(order.complete_date.day) == str(datetime.now().day):
            products = Prev_order_products.query\
                .filter_by(complete_order=order).all()
            for product in products:
                product_list = {}
                product_list["product_id"] = product.product_id
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                output.append(product_list)

    amt = []
    for i in range(0, len(output)):
        amt.append(int(output[i]["total_price"]))

    sum_amt = sum(amt)

    return jsonify({"success": "1",
                    "products_sold": output, "daily_sale": str(sum_amt)})


# the total sales of the current month and all the months in the current year
@vendor.route('/sales/month/current', methods=['GET'])
@login_required
def vendor_sales_month_current(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    output = []
    amt = []
    month_list = []
    if new_orders:
        for order in new_orders:
            if str(order.complete_date.year) == str(datetime.now().year):
                if not str(order.complete_date.month) in month_list:
                    month_list.append(str(order.complete_date.month))
            if str(order.complete_date.month) == str(datetime.now().month):
                products = Prev_order_products.query\
                    .filter_by(complete_order=order).all()
                for product in products:
                    amt.append(product.total_price)

        product_list = {}
        product_list["month"] = str(order.complete_date.month)
        product_list["sales"] = str(sum(amt))
        output.append(product_list)

        return jsonify({"success": "1",
                        "current_month_sold": output,
                        "month_list": month_list})

    return jsonify({"success": "0", "message": "No orders"})


# get the ratings of the vendor
@vendor.route('/ratings/show', methods=['GET'])
@login_required
def vendor_ratings_show(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    ratings = Vendor_rating.query.filter_by(vendor=ven).all()

    if ratings:

        rate = []
        for i in ratings:
            rate.append(i.rating)

        avg_rate = (sum(rate)/len(rate))

        return jsonify({"success": "1", "vendor_ratings": str(avg_rate)})

    return jsonify({"success": "0", "message": "No ratings Now"})


# get the month list of the current year
@vendor.route('/currentmonths', methods=['GET'])
@login_required
def vendor_amount(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    month_list = []
    for order in new_orders:
        if str(order.complete_date.year) == str(datetime.now().year):
            if not str(order.complete_date.month) in month_list:
                month_list.append(str(order.complete_date.month))

    return jsonify({"success": "1", "current_year_months": month_list})


# total sales according to month and the month list of the year requested
@vendor.route('/amount/months_list', methods=['GET'])
@login_required
def vendor_amount_months(current_user):

    year = request.args.get('year')

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    output = []
    month_list = []
    count = 0

    for order in new_orders:
        if str(order.complete_date.year) == year:
            count = 1
            if not str(order.complete_date.month) in month_list:
                month_list.append(str(order.complete_date.month))

    for i in month_list:
        month_amounts = {}
        total = month_sales_add(i, year, current_user.vendor_id)
        month_amounts["month"] = str(i)
        month_amounts["sales"] = total
        output.append(month_amounts)

    if count == 1:
        return jsonify({"success": "1",
                        "month_amount_list": output, "month_list": month_list})
    else:
        return jsonify({"success": "0", "message": "year not present"})


# function for adding monthly sales
def month_sales_add(month, year, vendor_id):

    new_orders = Prev_order.query.filter_by(vendor_details=vendor_id).all()

    add = []

    for order in new_orders:
        if str(order.complete_date.year) == year:
            if str(order.complete_date.month) == month:
                if not(order.total_bill) in add:
                    add.append(order.total_bill)

    total = sum(add)

    return total


# get the previous orders according to the year and month requested
@vendor.route('/order/previous/month', methods=['GET'])
@login_required
def vendor_order_pervious_month(current_user):

    data = request.args

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    output = []
    if new_orders:

        days_list = []

        for order in new_orders:
            if str(order.complete_date.year) == data['year']:
                if str(order.complete_date.month) == data['month']:
                    if not str(order.complete_date.day) in days_list:
                        days_list.append(str(order.complete_date.day))

        for i in days_list:
            total = day_sales(data['year'],
                              data['month'],
                              i, current_user.vendor_id)
            output.append(total)

        return jsonify({"success": "1", "Previous_Orders": output})

    return jsonify({"success": "0", "message": "No previous Orders"})


# sorting all the orders according to day in the month passed as argument
def day_sales(year, month, day, vendor_id):

    new_orders = Prev_order.query.filter_by(vendor_details=vendor_id).all()
    print("yes")

    day_wise = []

    for order in new_orders:
        if str(order.complete_date.year) == year:
            if str(order.complete_date.month) == month:
                if str(order.complete_date.day) == day:
                    output_data = {}
                    products_data = []
                    output_data["order_id"] = order.order_id
                    output_data["customer_id"] = order.customer_id
                    output_data["delivery_address"] = order.delivery_address
                    output_data["delivery_boy_id"] = order.delivery_boy_id
                    output_data["bill"] = str(order.bill)
                    output_data["total_bill"] = str(order.total_bill)
                    output_data["complete_date"] = order.complete_date
                    products = Prev_order_products.query\
                        .filter_by(complete_order=order).all()
                    for product in products:
                        product_list = {}
                        product_list["product_id"] = product.product_id
                        product_list["quantity"] = product.quantity
                        product_list["total_price"] = str(product.total_price)
                        products_data.append(product_list)
                    output_data["products"] = products_data
                    day_wise.append(output_data)

    return day_wise


# all the year list in the database
@vendor.route('/order/yearslist', methods=['GET'])
@login_required
def vendor_year_list(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()
    new_orders = Prev_order.query.filter_by(vendor=ven).all()

    year_list = []
    if new_orders:
        for order in new_orders:
            if not str(order.complete_date.year) in year_list:
                year_list.append(str(order.complete_date.year))

        return jsonify({"success": "1", "all_years": year_list})

    return jsonify({"success": "0", "message": "No years present"})


# get all the delivery boy of the vendor
@vendor.route('/delivery_boy/all', methods=['GET'])
@login_required
def vendor_deliverryBoy_list(current_user):

    ven = Vendor.query.filter_by(vendor_id=current_user.vendor_id)\
        .first()

    driver = Deliveryboy.query.filter_by(vendor=ven).all()

    if driver:

        output = []

        for boy in driver:
            drivers = {}
            drivers["driver_id"] = boy.driver_id
            drivers["email"] = boy.email
            drivers["name"] = boy.name
            drivers["age"] = str(boy.age)
            drivers["contact"] = boy.contact
            drivers["vehicle_type"] = boy.vehicle_type
            drivers["vehicle_number"] = boy.vehicle_number
            drivers["profile_img"] = url_for('static', filename='images/deliveryBoy_prof_pic/' + boy.prof_img)
            if boy.aadhar:
                drivers["aadhar"] = url_for('static', filename='images/deliveryBoy_aadhar_pic/' + boy.aadhar)
            else:
                drivers["aadhar"] = "no photo"
            output.append(drivers)

        return jsonify({"success": "1", "drivers": output})

    return jsonify({"success": "0", "message": "No driver Added till now!!"})


# vendor create new delivery boy
@vendor.route('/delivery_boy/create', methods=['POST'])
@login_required
def vendor_deliverryBoy_create(current_user):

    if request.is_json:

        data = request.get_json()

        alphabet = string.ascii_letters + string.digits
        driver_id = ''.join(random.choice(alphabet) for i in range(8))

        password = ''.join(str(random.randint(0, 10)) for i in range(5))

        hashed_password = generate_password_hash(password, method='sha256')

        new = Deliveryboy(driver_id=driver_id,
                          password=hashed_password,
                          name=data["name"],
                          age=int(data["age"]),
                          contact=data["contact"],
                          vehicle_type=data["vehicle_type"],
                          vehicle_number=data["vehicle_number"],
                          address=data["address"],
                          dob=data["dob"],
                          vendor_details=current_user.vendor_id)

        try:
            db.session.add(new)
            db.session.commit()

            return jsonify({"success": "1", "message": "Delivery boy created",
                            "password": password, "driver_id": driver_id})

        except Exception as e:
            db.session.rollback()
            print(e)

            return jsonify({"success": "0", "message": "could not save data"})

    return jsonify({"success": "0", "message": "request not right"})
