from flask import Blueprint, request, jsonify, url_for
from web import db
from web.models import Deliveryboy, Ongoing_order, Ongoing_order_products,\
    Prev_order, Prev_order_products, Customer, Vendor, Vendor_products,\
    Products, Customer
from web.utils import login_required, save_deliveryBoy_profpic,\
    send_push_customer, send_push_vendor, send_push_driver

delivery = Blueprint('Delivery', __name__)


# get the profile of the delivery boy
@delivery.route('/profile', methods=['GET'])
@login_required
def get_profile(current_user):

    driver = Deliveryboy.query.filter_by(driver_id=current_user.driver_id)\
        .first()

    drivers = {}
    drivers["driver_id"] = driver.driver_id
    drivers["name"] = driver.name
    drivers["age"] = str(driver.age)
    drivers["email"] = driver.email
    drivers["contact"] = driver.contact
    drivers["vehicle_type"] = driver.vehicle_type
    drivers["vehicle_number"] = driver.vehicle_number
    image_file = url_for('static',
                         filename='images/deliveryBoy_prof_pic/' + driver.prof_img)
    drivers["profile_img"] = image_file

    return jsonify({"success": "1", "driver_details": drivers})


# update the email of the delivery boy
@delivery.route('/profile/update/email', methods=['PUT'])
@login_required
def update_profile_email(current_user):
    if request.is_json:
        data = request.get_json()

        driver = Deliveryboy.query.filter_by(driver_id=current_user.driver_id)\
            .first()

        try:
            driver.email = data["email"].lower()
            db.session.commit()

            return jsonify({"success": "1", "message": "email updated"})
        except Exception as e:
            db.session.rollback()
            print(e)

            return jsonify({"success": "0",
                            "message": "could not update email"})

    return jsonify({"success": "0", "message": "request method is not right"})


# update the profile picture of the delivery boy
@delivery.route('/profile/update/prof_pic', methods=['PUT'])
@login_required
def update_profile_pic(current_user):

    file_name = request.files['file']
    img = save_deliveryBoy_profpic(file_name)

    driver = Deliveryboy.query.filter_by(driver_id=current_user.driver_id)\
        .first()

    try:
        driver.prof_img = img
        db.session.commit()

        return jsonify({"success": "1", "message": "profile pic updated"})
    except Exception as e:
        db.session.rollback()
        print(e)

        return jsonify({"success": "0",
                        "message": "could not update profile pic"})


# get current orders of delivery boy
@delivery.route('/ongoing_orders', methods=['GET'])
@login_required
def get_ongoingOrders(current_user):

    new_orders = Ongoing_order.query\
        .filter_by(delivery_boy_id=current_user.driver_id).all()

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
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                products_data.append(product_list)
            output_data["products"] = products_data
            output.append(output_data)

        return jsonify({"success": "1", "Ongoing_Orders": output})

    return jsonify({"success": "0", "message": "No ongoing Orders"})


# get delivered orders of delivery boy
@delivery.route('/delivered_orders', methods=['GET'])
@login_required
def get_deliveredOrders(current_user):

    new_orders = Prev_order.query\
        .filter_by(delivery_boy_id=current_user.driver_id).all()

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
                product_list["quantity"] = product.quantity
                product_list["total_price"] = str(product.total_price)
                products_data.append(product_list)
            output_data["products"] = products_data
            output.append(output_data)

        return jsonify({"success": "1", "Previous_Orders": output})

    return jsonify({"success": "0", "message": "No previous Orders"})


# pickup order to be delivered
@delivery.route('/order/pickup', methods=['PUT'])
@login_required
def pickup_order(current_user):
    if request.args:
        data = request.args.get('order_id')

        new_orders = Ongoing_order.query.filter_by(order_id=data)\
            .first()

        new_orders.pickup_status = True

        try:

            cust = Customer.query\
                .filter_by(customer_id=new_orders.customer_id).first()

            ven = Vendor.query.filter_by(vendor_id=new_orders.vendor_details)\
                .first()

            customer_message_title = "Order Picked Up By Delivery Boy"
            customer_message_body = f"Your order id: { new_orders.order_id }, has been picked up by: { current_user.name }!!"

            vendor_message_title = "Order Picked Up By Delivery Boy"
            vendor_message_body = f"Order id: { new_orders.order_id }, has been picked up by driver id: { current_user.driver_id }!!"

            res_customer = send_push_customer(customer_message_title,
                                              customer_message_body,
                                              cust.device_id)

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          ven.device_id)

            db.session.commit()

            return jsonify({"success": "1", "message": "Order Picked Up",
                            "cust_noti": res_customer, "ven_noti": res_vendor})

        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0",
                            "message": "could not be Order Picked Up"})

    return jsonify({"success": "0", "message": "data sent not correct format"})


# order delivered confirmation from the vendor
@delivery.route('/order/complete', methods=['POST'])
@login_required
def order_complete(current_user):
    if request.args:
        data = request.args

        new_orders = Ongoing_order.query\
            .filter_by(order_id=data['order_id'])\
            .first()

        if data['status'] == '1':
            new_orders.status = True
            curr_order = Prev_order(order_id=new_orders.order_id,
                                    customer_id=new_orders.customer_id,
                                    delivery_address=new_orders.delivery_address,
                                    delivery_boy_id=new_orders.delivery_boy_id,
                                    bill=new_orders.bill,
                                    total_bill=new_orders.total_bill,
                                    delivery_method=new_orders.delivery_method,
                                    vendor_details=new_orders.vendor_details)
            db.session.add(curr_order)
            products = Ongoing_order_products.query\
                .filter_by(ongoing_order=new_orders).all()
            for product in products:
                order_products = Prev_order_products(product_id=product.product_id,
                                                     quantity=product.quantity,
                                                     total_price=product.total_price,
                                                     order=data['order_id'])
                db.session.add(order_products)

            try:
                for i in products:
                    prod = Vendor_products.query\
                        .filter_by(vendor_details=new_orders.vendor_details,
                                   product_id=i.product_id).first()

                    prod.quantity_left = prod.quantity_left - i.quantity

                cust = Customer.query\
                    .filter_by(customer_id=new_orders.customer_id).first()

                vendor = Vendor.query\
                    .filter_by(vendor_id=new_orders.vendor_details).first()

                customer_message_title = "Order Delivered"
                customer_message_body = f"Your order id: { new_orders.order_id }, has been delivered successfully to you!!"

                vendor_message_title = "Order Delivered"
                vendor_message_body = f"Order id: { new_orders.order_id }, has been delivered by delievry boy id is: { current_user.driver_id }"

                driver_message_title = "Order Delivered"
                driver_message_body = f"Order id: { new_orders.order_id }, has been delivered succesfully!!"

                res_customer = send_push_customer(customer_message_title,
                                                  customer_message_body,
                                                  cust.device_id)

                res_vendor = send_push_vendor(vendor_message_title,
                                              vendor_message_body,
                                              vendor.device_id)

                res_driver = send_push_driver(driver_message_title,
                                              driver_message_body,
                                              current_user.device_id)

                db.session.delete(new_orders)
                db.session.commit()

                return jsonify({"success": "1", "message": "Order Received",
                                "cust_noti": res_customer,
                                "ven_noti": res_vendor,
                                "driv_noti": res_driver})
            except Exception as e:
                print(e)
                db.session.rollback()

                return jsonify({"success": "0", "message": "error ocurred"})

    return jsonify({"success": "0", "message": "data sent not correct"})
