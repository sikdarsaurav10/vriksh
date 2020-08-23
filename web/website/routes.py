import string
import random
from flask import request, redirect, url_for, render_template, flash, jsonify
from web import db
from web.website.views import website
from web.models import Customer, Cart, Products, New_order,\
    New_order_products, Vendor, Vendor_products, Ongoing_order,\
    Cityandcharge, Complaints, Feedback, Vendor_rating, Productratings
from web.utils import find_coord, select_vendor, send_push_vendor
import uuid
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user


# reroute to landing page with the city
@website.route('/getcity',  methods=['POST'])
def web_landing():
    city = request.form['city']
    return redirect(url_for('Website.get_landing_page', city=city))


# register page for the customer
@website.route('/register/customer', methods=['GET', 'POST'])
def register_web():
    city = Cityandcharge.query.all()
    cities = []
    for item in city:
        if item.city not in cities:
            cities.append(item.city)
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['last_name']
        email = request.form['email']
        contact_one = request.form['contact_one']
        contact_two = request.form['contact_two']
        houseNo = request.form['house_no']
        landmark = request.form['landmark']
        locality = request.form['locality']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pinCode']
        password = request.form['pass']

        cust = Customer.query.filter_by(email=email.lower()).first()

        if cust:
            flash("You are already a Customer, PLease Log in", "warning")
            return redirect(url_for('Website.login_web'))

        name = f_name+" "+l_name
        hashed_password = generate_password_hash(password,
                                                 method='sha256')
        customer_id = str(uuid.uuid4())
        address = landmark+", "+locality+", "+city+", "+state+" "+pincode
        arr = find_coord(address)

        if contact_two == "":

            new_customer = Customer(customer_id=customer_id,
                                    email=email.lower(),
                                    password=hashed_password,
                                    name=name,
                                    contact_one=contact_one,
                                    const_house_no=houseNo,
                                    const_landmark=landmark.lower(),
                                    const_locality=locality.lower(),
                                    const_city=city.lower(),
                                    const_state=state.lower(),
                                    const_pincode=pincode,
                                    delivery_house_no=houseNo,
                                    delivery_landmark=landmark.lower(),
                                    delivery_locality=locality.lower(),
                                    delivery_city=city.lower(),
                                    delivery_state=state.lower(),
                                    delivery_pincode=pincode,
                                    latitude=arr[0],
                                    longitude=arr[1])
        else:
            new_customer = Customer(customer_id=customer_id,
                                    email=email,
                                    password=hashed_password,
                                    name=name,
                                    contact_one=contact_one,
                                    contact_two=contact_two,
                                    const_house_no=houseNo,
                                    const_landmark=landmark.lower(),
                                    const_locality=locality.lower(),
                                    const_city=city.lower(),
                                    const_state=state.lower(),
                                    const_pincode=pincode,
                                    delivery_house_no=houseNo,
                                    delivery_landmark=landmark.lower(),
                                    delivery_locality=locality.lower(),
                                    delivery_city=city.lower(),
                                    delivery_state=state.lower(),
                                    delivery_pincode=pincode,
                                    latitude=arr[0],
                                    longitude=arr[1])

        try:
            db.session.add(new_customer)
            db.session.commit()

            flash("Register successfull!, Please Login to continue", "success")
            return redirect(url_for('Website.login_web'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("Error Occured, PLease try Again", "danger")
            return render_template('web_view/register.html')
    return render_template('web_view/register.html', cities=cities)


# add products to cart
@website.route('/customer/web/cart/add/new', methods=['POST'])
@login_required
def web_cart_add():
    if request.is_json:
        data = request.get_json()
        pr = Cart.query\
            .filter_by(customer_details=current_user.customer_id,
                       product_id=data["product_id"]).first()

        if pr:
            return jsonify({"success": "0", "message": "Item already in cart"})

        new = Cart(product_id=data["product_id"],
                   quantity=1,
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


# increase product quantity
@website.route('/customer/web/cart/increase', methods=['PUT'])
@login_required
def web_cart_increase():
    data = request.get_json()
    item = Cart.query\
        .filter_by(customer_details=current_user.customer_id,
                   product_id=data["product_id"]).first()

    try:
        item.quantity = item.quantity + 1
        db.session.commit()

        return jsonify({"success": "1", "quantity": item.quantity})
    except Exception as e:
        print(e)
        db.session.rollback()

        return jsonify({"success": "0",
                        "message": "quantity not increased"})


# decrease product quantity
@website.route('/customer/web/cart/decrease', methods=['PUT'])
@login_required
def web_cart_decrease():
    data = request.get_json()
    item = Cart.query\
        .filter_by(customer_details=current_user.customer_id,
                   product_id=data["product_id"]).first()

    try:
        item.quantity = item.quantity - 1
        db.session.commit()
        if item.quantity == 0:
            db.session.delete(item)
            db.session.commit()
            return jsonify({"success": "2"})
        return jsonify({"success": "1", "quantity": item.quantity})
    except Exception as e:
        print(e)
        db.session.rollback()

        return jsonify({"success": "0",
                        "message": "quantity not increased"})


# send amount details of the cart of the customer
@website.route('/customer/web/cart/amt')
@login_required
def web_cart_amt():
    cart = Cart.query\
        .filter_by(customer_details=current_user.customer_id).all()
    charge = Cityandcharge.query\
        .filter_by(city=current_user.const_city).first()
    if cart:
        totalPrice = []
        totalAmt = []
        totalDiscount = []
        for item in cart:
            product = Products.query.filter_by(product_id=item.product_id)\
                .first()
            if product.offer > 0:
                i = (product.discount - int((product.discount) * (product.offer / 100)))
                totalAmt.append((i*item.quantity))
            else:
                totalAmt.append((product.discount*item.quantity))
            totalPrice.append(product.price*item.quantity)
            totalDiscount.append(product.offer)

        totalBill = sum(totalAmt) + charge.delivery_charge

        return jsonify({"success": "1",
                        "price": sum(totalPrice),
                        "amt": sum(totalAmt),
                        "offer": sum(totalDiscount),
                        "bill": totalBill,
                        "charge": charge.delivery_charge})

    return jsonify({"success": "0", "message": "nothing in cart"})


# get amt of individual item
@website.route('/cart/item/amount/<product_id>')
@login_required
def price_item(product_id):
    pr = Products.query.filter_by(product_id=product_id).first()
    item = Cart.query\
        .filter_by(customer_details=current_user.customer_id,
                   product_id=product_id).first()
    original_amt = pr.price * item.quantity
    amt = pr.discount * item.quantity

    return jsonify({"success": "1",
                    "original_amt": original_amt,
                    "amt": amt})


# plcae order of cart
@website.route('/customer/web/cart/place', methods=['POST'])
@login_required
def web_place_order():
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

            vendor_message_title = "Order Received"
            vendor_message_body = f"order id: { order_id } received,Please open new orders in app to view details"

            vendor_res = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          ven.device_id)

            return jsonify({"success": "1", "Order_Added": order_id,
                            "ven_noti": vendor_res})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Order not places, failed"})

    return jsonify({"succes": "0",
                    "message": "data sent not correct format"})


# cancel ongoing orders
@website.route('/customer/web/ongoing/cancel')
def web_cancel_order():
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
                vendor_message_title = "Order Declined"
                vendor_message_body = f"Order id: { new_orders.order_id }, has been cancelled by the customer!!"

            elif new_orders_one:
                vendor_message_title = "Order Declined"
                vendor_message_body = f"Order id: { new_orders_one.order_id }, has been cancelled by the customer!!"

            res_vendor = send_push_vendor(vendor_message_title,
                                          vendor_message_body,
                                          ven.device_id)

            if new_orders:
                db.session.delete(new_orders)
            elif new_orders_one:
                db.session.delete(new_orders_one)

            db.session.commit()

            return redirect(url_for('Website.get_web_ongoing_order'))

        except Exception as e:
            print(e)
            db.session.rollback()

            return redirect(url_for('Website.get_web_ongoing_order'))


# profile of the customer
# faq on profile page

# submit complain from customer
@website.route('/web/complain/<order_id>/<vendor_id>', methods=['POST'])
@login_required
def complains_new_web(order_id, vendor_id):
    title = request.form['title']
    description = request.form['description']

    alphabet = string.ascii_letters + string.digits
    complain_id = ''.join(random.choice(alphabet) for i in range(7))

    new = Complaints(complain_id=complain_id,
                     order_id=order_id,
                     customer_id=current_user.customer_id,
                     title=title,
                     description=description,
                     vendor_details=vendor_id)

    try:
        db.session.add(new)
        db.session.commit()

        flash('Complaint Sended to Vendor', "success")
        return redirect(url_for('Website.web_complain',
                                order_id=order_id,
                                vendor_id=vendor_id))
    except Exception as e:
        print(e)
        db.session.rollback()

        flash('Error, Please Try Again', "danger")
        return redirect(url_for('Website.web_complain',
                                order_id=order_id,
                                vendor_id=vendor_id))


# submit feedback from customer
@website.route('/web/feedback', methods=['POST'])
@login_required
def feedback_new_web():
    description = request.form['description']
    feed = Feedback(customer_id=current_user.customer_id,
                    description=description)

    try:
        db.session.add(feed)
        db.session.commit()

        flash('Feedback Submited', "success")
        return redirect(url_for('Website.web_feedback'))
    except Exception as e:
        print(e)
        db.session.rollback()

        flash('Error, Please Try Again', "danger")
        return redirect(url_for('Website.web_feedback'))


# submit rating for the vendor
@website.route('/web/ratings/new', methods=['POST'])
@login_required
def ratings_new_web():
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
@website.route('/web/ratings/products', methods=['POST'])
@login_required
def ratings_products_web():
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
