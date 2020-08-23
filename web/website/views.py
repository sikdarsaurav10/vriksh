from flask import Blueprint, render_template, url_for, redirect, flash, request
from web.models import Products, Vendor_products, Vendor, Productratings,\
    Customer, Cart, New_order, New_order_products, Ongoing_order,\
    Ongoing_order_products, Vendor_rating, Prev_order, Prev_order_products
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

website = Blueprint('Website', __name__)


# index page
@website.route('/')
def web_index():
    product = Products.query.all()
    return render_template('web_view/index.html', product=product)


# get the landing page of the customer
@website.route('/landing/<city>')
def get_landing_page(city):

    categories = get_category(city)

    return render_template('web_view/landing_page.html', categories=categories,
                           city=city)


def get_category(city):
    ven = Vendor.query.filter_by(city=city).all()

    categories = []

    if ven:
        for vendor in ven:
            products = Vendor_products.query\
                .filter_by(vendor=vendor).all()

            for item in products:
                if item.category not in categories:
                    categories.append(item.category)
    return categories


# get to the all products details page
@website.route('/products/<city>/<category_name>')
def get_products_all(city, category_name):
    title = category_name + ' | Products'
    categories = get_category(city)
    ven = Vendor.query.filter_by(city=city).all()

    categories = []
    products = []
    available_products = []
    finished_products = []
    output = []

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

    if category_name == "all":

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

    elif category_name == "offer":

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

    else:

        for i in products:
            items = Products.query.filter_by(product_id=i).first()
            if items.category_name == category_name:
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

    return render_template('web_view/web_products.html',
                           title=title,
                           city=city,
                           category_name=category_name,
                           categories=categories,
                           output=output)


# get the product detail Page
@website.route('/product/details/<city>/<product_id>')
def get_product_detailPage(product_id, city):

    product = Products.query.filter_by(product_id=product_id).first()

    print(product.product_name)
    title = product.product_name
    categories = get_category(city)

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

    return render_template('web_view/product_detail_page.html',
                           title=title,
                           categories=categories,
                           city=city,
                           output=output_data)


# privacy policy page
@website.route('/privacyPol/<city>')
def web_privacy_pol(city):
    title = "Privacy Policy"
    categories = get_category(city)
    return render_template('web_view/web_privacy_pol.html',
                           title=title,
                           categories=categories,
                           city=city)


# Terms and Condition page
@website.route('/terms&cond/<city>')
def web_terms_cond(city):
    title = "Terms and Condition"
    categories = get_category(city)
    return render_template('web_view/web_terms_cond.html',
                           title=title,
                           categories=categories,
                           city=city)


# about us page
@website.route('/about/<city>')
def web_about(city):
    title = "About Us"
    categories = get_category(city)
    return render_template('web_view/web_about.html',
                           title=title,
                           categories=categories,
                           city=city)


# login page for the customer
@website.route('/login/customer/web', methods=['GET', 'POST'])
def login_web():
    if current_user.is_authenticated:
        return redirect(url_for('Website.get_landing_page',
                        city=current_user.const_city))
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["pass"]

        cust = Customer.query.filter_by(email=email.lower()).first()

        if cust and check_password_hash(cust.password, pwd):
            login_user(cust)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('Website.get_landing_page', city=cust.const_city))
        else:
            flash('Not authorised!!', 'danger')
            return redirect(url_for('Website.login_web'))
    return render_template('web_view/log_in.html')


# cart view for customer
@website.route('/customer/web/cart')
@login_required
def web_cart():
    title = 'Cart | ' + current_user.name
    categories = get_category(current_user.const_city)
    cart = Cart.query\
        .filter_by(customer_details=current_user.customer_id).all()
    output = []
    if cart:
        for item in cart:
            product = Products.query.filter_by(product_id=item.product_id)\
                .first()
            product_data = {}
            product_data["product_id"] = product.product_id
            product_data["category"] = product.category_name
            product_data["product_name"] = product.product_name
            product_data["img"] = product.prof_img
            product_data["price"] = product.price
            product_data["discounted_price"] = product.discount
            product_data["offer"] = product.offer
            product_data["quantity"] = item.quantity
            output.append(product_data)

    return render_template('web_view/web_cart.html',
                           title=title,
                           categories=categories,
                           city=current_user.const_city,
                           output=output)


# show ongoing and new orders of the customer
@website.route('/customer/web/order/ongoing')
@login_required
def get_web_ongoing_order():

    title = "Ongoing Order "+current_user.name
    categories = get_category(current_user.const_city)
    new_orders = New_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    ongoing_orders = Ongoing_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    new_output = []
    if new_orders:
        for order in new_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["delivery_address"] = order.delivery_address
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_date"] = order.order_date
            # output_data["vendor_id"] = order.vendor_details
            products = New_order_products.query\
                .filter_by(new_order=order).all()
            for product in products:
                product_list = {}
                item = Products.query\
                    .filter_by(product_id=product.product_id).first()
                product_list["product_id"] = product.product_id
                product_list["product_name"] = item.product_name
                product_list["offer"] = item.offer
                product_list["prof_img"] = item.prof_img
                product_list["quantity"] = product.quantity
                product_list["total_price"] = product.total_price
                products_data.append(product_list)
            output_data["products"] = products_data
            new_output.append(output_data)

    ongoing_output = []
    if ongoing_orders:
        for order in ongoing_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["total_bill"] = str(order.total_bill)
            output_data["order_approve_date"] = order.order_approve_date
            output_data["pickup_status"] = order.pickup_status
            # output_data["vendor_id"] = order.vendor_details
            products = Ongoing_order_products.query\
                .filter_by(ongoing_order=order).all()
            for product in products:
                product_list = {}
                item = Products.query\
                    .filter_by(product_id=product.product_id).first()
                product_list["product_id"] = product.product_id
                product_list["product_name"] = item.product_name
                product_list["offer"] = item.offer
                product_list["prof_img"] = item.prof_img
                product_list["quantity"] = product.quantity
                product_list["total_price"] = product.total_price
                products_data.append(product_list)
            output_data["products"] = products_data
            ongoing_output.append(output_data)

    return render_template('web_view/web_ongoing_orders.html',
                           title=title,
                           new_order=new_output,
                           ongoing_order=ongoing_output,
                           city=current_user.const_city,
                           categories=categories)


# get previous orders of the customer
@website.route('/customer/web/order/previous')
@login_required
def get_web_prev_order():

    title = "Completed Order "+current_user.name
    categories = get_category(current_user.const_city)
    prev_orders = Prev_order.query\
        .filter_by(customer_id=current_user.customer_id).all()

    prev_output = []
    if prev_orders:

        for order in prev_orders:
            output_data = {}
            products_data = []
            output_data["order_id"] = order.order_id
            output_data["delivery_address"] = order.delivery_address
            output_data["delivery_boy_id"] = order.delivery_boy_id
            output_data["total_bill"] = order.total_bill
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
                product_list["prof_img"] = item.prof_img
                product_list["quantity"] = product.quantity
                product_list["total_price"] = product.total_price
                products_data.append(product_list)
            output_data["products"] = products_data
            prev_output.append(output_data)

    return render_template('web_view/web_previous_orders.html',
                           title=title,
                           prev_order=prev_output,
                           city=current_user.const_city,
                           categories=categories)


# complain page of order
@website.route('/web/complain/get/<order_id>/<vendor_id>')
@login_required
def web_complain(order_id, vendor_id):
    title = "Complaint "+order_id
    categories = get_category(current_user.const_city)
    return render_template('web_view/web_complain.html',
                           title=title,
                           order_id=order_id,
                           vendor_id=vendor_id,
                           categories=categories,
                           city=current_user.const_city)


# send feedback
@website.route('/web/feedback/get')
@login_required
def web_feedback():
    title = "Submit Feedback"
    categories = get_category(current_user.const_city)
    return render_template('web_view/web_feedback.html',
                           title=title,
                           categories=categories,
                           city=current_user.const_city)


# profile page of customer
@website.route('/customer/profile/web')
@login_required
def profile_web():
    title = "Profile "+current_user.customer_id
    categories = get_category(current_user.const_city)
    return render_template('web_view/web_profile.html',
                           title=title,
                           categories=categories,
                           city=current_user.const_city)


# logout user
@website.route('/customer/web/logout')
def logout_web():
    logout_user()
    return redirect(url_for('Website.web_index'))
