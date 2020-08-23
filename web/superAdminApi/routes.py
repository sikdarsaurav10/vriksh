import random
import string
from flask import Blueprint, request, jsonify, render_template, redirect,\
    url_for, flash, session
from web import db
from web.models import Admin, Products, Vendor, Vendor_products, Complaints,\
    Products, Customer, Prev_order, Feedback, Promotionalcodes, Category,\
    About, Privacypolicy, Faq, Bannerimages, Cityandcharge
from web.utils import save_product_pic, save_category_pic,\
    send_reset_email, save_banner_pic, send_push_vendor
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


admin = Blueprint('Admin', __name__)


# login page for admin
@admin.route('/signin', methods=['GET', 'POST'])
def log_in():
    if 'id' in session:
        return redirect(url_for('Admin.home_page'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Admin.query.filter_by(email=email).first()
        if not user:
            flash("You are not an Admin!!", "warning")
            return render_template('admin/log_in.html')

        if check_password_hash(user.password, password):
            session["id"] = user.admin_id
            return redirect(url_for('Admin.home_page'))
        else:
            flash("Password is incorrect", "danger")
            return render_template('admin/log_in.html')
    return render_template('admin/log_in.html')


# forgot password view
@admin.route('/forgot/password', methods=['GET', "POST"])
def forgot_password_admin():
    title = "Reset Password"
    if 'id' in session:
        return redirect(url_for('Admin.home_page'))
    if request.method == 'POST':
        email = request.form['recoveryEmail']
        user = Admin.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("An email has been sent to reset the password", "info")
            return redirect(url_for('Admin.log_in'))
        flash("Not registered email!!", "warning")
        return render_template('admin/forgot_password_admin.html',
                               title=title)
    return render_template('admin/forgot_password_admin.html',
                           title=title)


# reset password with token
@admin.route('/forgot/password/<token>', methods=['GET', "POST"])
def reset_password_admin(token):
    title = "Reset Password"
    if 'id' in session:
        return redirect(url_for('Admin.home_page'))
    user = Admin.verify_reset_token(token)
    if not user:
        flash("This is a invalid or expired token", "warning")
        return redirect(url_for('Admin.forgot_password_admin'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        if password == confirm_password:

            hashed_password = generate_password_hash(password,
                                                     method='sha256')
            user.password = hashed_password
            try:
                db.session.commit()

                flash("Password changed Successfully!", "success")
                return redirect(url_for('Admin.log_in'))
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("There was an error, Please try again!!",
                      "warning")
                return render_template('admin/forgot_password_admin_change.html',
                                       title=title)

    return render_template('admin/forgot_password_admin_change.html',
                           title=title)


# admin landing page
@admin.route('/home')
def home_page():
    if 'id' in session:
        return render_template('admin/admin_index.html')
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin orders Page
@admin.route('/orders')
def show_orders():
    title = "Orders Summary | Admin"
    if 'id' in session:
        orders = Prev_order.query.all()
        return render_template('admin/admin_orders.html',
                               title=title,
                               orders=orders)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin Products Page
@admin.route('/products')
def show_products():
    title = "All Products | Admin"
    if 'id' in session:
        product = Products.query.all()
        category = Category.query.all()
        return render_template('admin/admin_products.html',
                               title=title,
                               product=product,
                               category=category)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin Customers Page
@admin.route('/customers')
def show_customers():
    title = "All customers | Admin"
    if 'id' in session:
        customer = Customer.query.all()
        return render_template('admin/admin_customers.html',
                               title=title,
                               customer=customer)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin vendors Page
@admin.route('/vendors')
def show_vendors():
    title = "All vendors | Admin"
    if 'id' in session:
        vendors = Vendor.query\
            .filter_by(vendor_status=True).all()
        return render_template('admin/admin_vendors.html',
                               title=title,
                               vendors=vendors)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# get new vendor request
@admin.route('vendor/newRequest')
def get_vendor_request():
    title = "New Vendor Request | Admin"
    if 'id' in session:
        ven = Vendor.query.filter_by(vendor_status=False).all()
        if ven:
            return render_template('admin/admin_vendor_request.html',
                                   title=title,
                                   vendor=ven)
        flash("No new Vendor Request", "primary")
        return render_template('admin/admin_vendor_request.html',
                               title=title)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# accept vendor request
@admin.route('/vendor/add/new')
def add_vendor():
    if 'id' in session:
        if request.args:
            data = request.args

            if data["status"] == "0":
                ven = Vendor.query\
                    .filter_by(vendor_id=data["vendor_id"]).first()

                try:
                    db.session.delete(ven)
                    db.session.commit()

                    flash("Vendor Request Denied", "danger")
                    return redirect(url_for('Admin.get_vendor_request'))
                except Exception as e:
                    print(e)
                    db.session.rollback()

                    flash("Error Deleting, Please Try Again!",
                          "warning")
                    return redirect(url_for('Admin.get_vendor_request'))

            elif data["status"] == "1":
                ven = Vendor.query\
                    .filter_by(vendor_id=data["vendor_id"]).first()

                try:
                    ven.vendor_status = True

                    db.session.commit()

                    flash("Vendor Request Accepted", "success")
                    return redirect(url_for('Admin.get_vendor_request'))
                except Exception as e:
                    print(e)
                    db.session.rollback()

                    flash("Error Deleting, Please Try Again!",
                          "warning")
                    return redirect(url_for('Admin.get_vendor_request'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove vendor from the list
@admin.route('/vendor/remove')
def remove_vendor():
    if 'id' in session:

        ven_id = request.args.get('vendor_id')

        ven = Vendor.query.filter_by(vendor_id=ven_id).first()

        try:
            db.session.delete(ven)
            db.session.commit()

            flash("Vendor Deleted", "success")
            return redirect(url_for('Admin.show_vendors'))

        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Vendor Could not be Deleted", "warning")
            return redirect(url_for('Admin.show_vendors'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# see the vendor products
@admin.route('/vendor/products/show')
def get_vendor_product():
    if 'id' in session:
        data = request.args.get('vendor_id')

        ven = Vendor.query.filter_by(vendor_id=data)\
            .first()

        products = Vendor_products.query\
            .filter_by(vendor=ven).all()

        title = ven.name+" Products | Admin"
        if products:
            return render_template('admin/admin_vendor_products.html',
                                   title=title,
                                   products=products,
                                   vendor=ven.name,
                                   vendor_id=ven.vendor_id)
        flash("No Products Till Now", "warning")
        return render_template('admin/admin_vendor_products.html',
                               title=title,
                               vendor=ven.name)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin complains Page
@admin.route('/complains')
def show_complains():
    title = "All complains | Admin"
    if 'id' in session:
        complains = Complaints.query.all()
        return render_template('admin/admin_complains.html',
                               title=title,
                               complains=complains)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# admin feedback Page
@admin.route('/feedback')
def show_feedbacks():
    title = "All feedback | Admin"
    if 'id' in session:
        feedback = Feedback.query.all()
        return render_template('admin/admin_feedbacks.html',
                               title=title,
                               feedback=feedback)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for banner images
@admin.route('/banner_images')
def get_banner_page():
    title = "Banner Images | Admin"
    if 'id' in session:
        images = Bannerimages.query.get(1)
        if images:
            return render_template('admin/banner_images.html',
                                   title=title,
                                   images=images)
        flash("No image till Now", "info")
        return render_template('admin/banner_images.html',
                               title=title)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# upload banner imaegs
@admin.route('/banner_images/upload', methods=['POST'])
def upload_banner_images():
    if 'id' in session:
        image_num = request.args.get('image')
        pic = Bannerimages.query.get(1)

        img = request.files["image"]
        file_name = save_banner_pic(img)

        if image_num == "one":
            if pic:
                pic.image_1 = file_name
            else:
                new = Bannerimages(image_1=file_name)
                db.session.add(new)
        elif image_num == "two":
            if pic:
                pic.image_2 = file_name
            else:
                new = Bannerimages(image_2=file_name)
                db.session.add(new)
        elif image_num == "three":
            if pic:
                pic.image_3 = file_name
            else:
                new = Bannerimages(image_3=file_name)
                db.session.add(new)
        elif image_num == "four":
            if pic:
                pic.image_4 = file_name
            else:
                new = Bannerimages(image_4=file_name)
                db.session.add(new)
        elif image_num == "five":
            if pic:
                pic.image_5 = file_name
            else:
                new = Bannerimages(image_5=file_name)
                db.session.add(new)

        try:
            db.session.commit()

            flash("Image Uploaded Successfully", "success")
            return redirect(url_for('Admin.get_banner_page'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Could not upload, Please Try again!!", "danger")
            return redirect(url_for('Admin.get_banner_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for changing password
@admin.route('/password/change', methods=['GET', 'POST'])
def change_password():
    title = "Change Password | Admin"

    if 'id' in session:
        if request.method == 'POST':
            password = request.form['password']
            confirm_password = request.form['confirmPassword']
            if password == confirm_password:

                hashed_password = generate_password_hash(password,
                                                         method='sha256')
                user = Admin.query.filter_by(admin_id=session["id"]).first()
                if user:
                    user.password = hashed_password
                    try:
                        db.session.commit()

                        flash("Password changed Successfully!", "success")
                        return render_template('admin/password_change.html',
                                               title=title)
                    except Exception as e:
                        print(e)
                        db.session.rollback()
                        flash("There was an error, Please try again!!",
                              "warning")
                        return render_template('admin/password_change.html',
                                               title=title)
            flash("Both the fields do not match", "warning")
            return render_template('admin/password_change.html', title=title)

        return render_template('admin/password_change.html', title=title)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for promotional Codes
@admin.route('/promotional_codes')
def get_codes_page():
    title = "Promotional Codes | Admin"
    if 'id' in session:
        promo = Promotionalcodes.query.all()
        return render_template('admin/promotional_codes.html',
                               title=title,
                               promo=promo)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# create promo code
@admin.route('/promotional_codes/new', methods=['POST'])
def create_code():
    if 'id' in session:
        name = request.form['code']
        amt = request.form['discount']

        new = Promotionalcodes(code=name, discount=int(amt))

        try:
            db.session.add(new)
            db.session.commit()

            return redirect(url_for('Admin.get_codes_page'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Promo Code Not created. Please try again")
            return redirect(url_for('Admin.get_codes_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove promo code
@admin.route('/promotional_codes/remove')
def remove_code():
    if 'id' in session:

        promo = request.args.get('code')

        remove = Promotionalcodes.query.filter_by(code=promo).first()

        try:
            db.session.delete(remove)
            db.session.commit()

            return redirect(url_for('Admin.get_codes_page'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Promo Code Not be removed. Please try again")
            return redirect(url_for('Admin.get_codes_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for admin creation
@admin.route('/new')
def get_admin_page():
    title = "Create Admin | Admin"
    if 'id' in session:
        return render_template('admin/create_admin.html',
                               title=title)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for about section
@admin.route('/about_section')
def get_about_page():
    title = "About Section | Admin"
    if 'id' in session:
        about = About.query.get(1)
        return render_template('admin/about_section.html',
                               title=title,
                               about=about)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# to update the about section
@admin.route('/about_section/add', methods=['POST'])
def update_about():
    if 'id' in session:

        description = request.form["description"]

        about = About.query.get(1)
        if about:
            about.description = description

            try:
                db.session.commit()

                flash("About section has been updated", "success")
                return redirect(url_for('Admin.get_about_page'))
            except Exception as e:
                print(e)
                db.session.rollback()

                flash("About section couldn't be updated. Please try again",
                      "danger")
                return redirect(url_for('Admin.get_about_page'))

        else:
            new = About(description=description)

            try:
                db.session.add(new)
                db.session.commit()

                flash("About section has been updated", "success")
                return redirect(url_for('Admin.get_about_page'))
            except Exception as e:
                print(e)
                db.session.rollback()

                flash("About section couldn't be updated. Please try again",
                      "danger")
                return redirect(url_for('Admin.get_about_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for privacy section
@admin.route('/privacy_section')
def get_privacy_page():
    title = "Privacy Policy Section | Admin"
    if 'id' in session:
        privacy = Privacypolicy.query.all()
        return render_template('admin/privacy_section.html', title=title,
                               privacy=privacy)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# to update the privacy section
@admin.route('/privacy_section/add', methods=['POST'])
def update_privacy():
    if 'id' in session:

        title = request.form["title"]
        description = request.form["description"]

        new = Privacypolicy(title=title, description=description)

        try:
            db.session.add(new)
            db.session.commit()

            flash("Privacy Policy added", "success")
            return redirect(url_for('Admin.get_privacy_page'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Privacy Policy couldn't be added. Please try again",
                  "danger")
            return redirect(url_for('Admin.get_privacy_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove the privacy policy
@admin.route('/privacy_section/remove')
def remove_privacy():
    if 'id' in session:
        if request.args:
            no = request.args.get('id')

            new = Privacypolicy.query.get(int(no))

            try:
                db.session.delete(new)
                db.session.commit()

                flash("Privacy Policy removed", "success")
                return redirect(url_for('Admin.get_privacy_page'))

            except Exception as e:
                print(e)
                db.session.rollback()

                flash("Privacy Policy couldn't be deleted. Please try again",
                      "danger")
                return redirect(url_for('Admin.get_privacy_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view for faq section
@admin.route('/faq_section')
def get_faq_page():
    title = "FAQ Section | Admin"
    if 'id' in session:
        faq = Faq.query.all()
        return render_template('admin/faq_section.html', title=title,
                               faq=faq)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# to update the faq section
@admin.route('/faq_section/add', methods=['POST'])
def update_faq():
    if 'id' in session:

        title = request.form["title"]
        description = request.form["description"]

        new = Faq(title=title, description=description)

        try:
            db.session.add(new)
            db.session.commit()

            flash("FAQ added", "success")
            return redirect(url_for('Admin.get_faq_page'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("FAQ couldn't be added. Please try again", "danger")
            return redirect(url_for('Admin.get_faq_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove the faq policy
@admin.route('/faq_section/remove')
def remove_faq():
    if 'id' in session:
        if request.args:
            no = request.args.get('id')

            new = Faq.query.get(int(no))

            try:
                db.session.delete(new)
                db.session.commit()

                flash("FAQ removed", "success")
                return redirect(url_for('Admin.get_faq_page'))

            except Exception as e:
                print(e)
                db.session.rollback()

                flash("FAQ couldn't be deleted. Please try again",
                      "danger")
                return redirect(url_for('Admin.get_faq_page'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# create new admin
@admin.route('/new/create', methods=['POST'])
def create_admin():
    data = request.get_json()

    admin = Admin.query.filter_by(email=data["email"]).first()
    print(data["email"])
    if admin:
        return jsonify({"success": "2",
                        "message": "admin already exist"})

    hashed_password = generate_password_hash(data["password"], method='sha256')

    new_user = Admin(admin_id=str(uuid.uuid4()),
                     email=data["email"],
                     password=hashed_password,
                     name=data["name"])

    try:
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": "1",
                        "message": "New admin created"})
    except Exception as e:
        print(e)
        db.session.rollback()

        return jsonify({"success": "0",
                        "message": "New admin not created"})


# get the category of the products
@admin.route('/category')
def show_category():
    title = "Categories of Products | Admin"
    if 'id' in session:
        category = Category.query.all()
        return render_template('admin/admin_category.html', title=title,
                               category=category)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# add category of the products
@admin.route('/category/new', methods=['POST'])
def create_category():
    if 'id' in session:

        name = request.form["name"]

        img = request.files["image"]
        file_name = save_category_pic(img)

        new_category = Category(name=name,
                                prof_img=file_name)
        try:
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('Admin.show_category'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Category Not Created!!, Please try again", "warning")
            return redirect(url_for('Admin.show_category'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# update category of the products
@admin.route('/category/update')
def update_category():
    if 'id' in session:
        return ''
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove category of the products
@admin.route('/category/remove')
def remove_category():
    if 'id' in session:

        name = request.args.get('category_name')

        cat = Category.query.filter_by(name=name).first()
        ven = Vendor_products.query.filter_by(category=name).all()

        if ven:
            for item in ven:
                db.session.delete(item)

        try:
            db.session.delete(cat)
            db.session.commit()

            return redirect(url_for('Admin.show_category'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Category Not Deleted!!, Please try again", "warning")
            return redirect(url_for('Admin.show_category'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# add new product to the product list
@admin.route('/product/new', methods=['POST'])
def new_product():
    if 'id' in session:

        category = request.form["category"]
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        discount = request.form["discount"]

        img = request.files["image"]
        file_name = save_product_pic(img)

        alphabet = string.ascii_letters + string.digits
        product_id = ''.join(random.choice(alphabet) for i in range(10))

        new_product = Products(product_id=product_id,
                               product_name=name,
                               description=description,
                               prof_img=file_name,
                               price=int(price),
                               discount=int(discount),
                               category_name=category)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('Admin.show_products'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# update view for the products
@admin.route('product/update')
def get_update_product():
    if 'id' in session:
        title = "Update Product Info | Admin"
        if request.args:
            pr_id = request.args.get('product_id')
            product = Products.query.filter_by(product_id=pr_id).first()

            return render_template('admin/update_admin_product.html',
                                   title=title,
                                   product=product)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# update product info
@admin.route('/product/update/new', methods=['POST'])
def update_product():
    if 'id' in session:

        pr_id = request.args.get('product_id')
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        discount = request.form["discount"]

        product = Products.query.filter_by(product_id=pr_id).first()
        ven = Vendor_products.query.filter_by(product_id=pr_id).all()

        product.product_name = name
        product.description = description
        product.price = int(price)
        product.discount = int(discount)

        if ven:
            for item in ven:
                item.product_name = name
                item.description = description
                item.price = int(price)
                item.discount = int(discount)

        db.session.commit()

        flash('Product Info Updated', "success")
        return redirect(url_for('Admin.show_products'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove product from the list
@admin.route('/product/remove')
def remove_product():
    if 'id' in session:

        pr_id = request.args.get('product_id')

        product = Products.query.filter_by(product_id=pr_id).first()
        ven = Vendor_products.query.filter_by(product_id=pr_id).all()

        if ven:
            for item in ven:
                db.session.delete(item)

        db.session.delete(product)
        db.session.commit()

        flash('Product Deleted', "success")
        return redirect(url_for('Admin.show_products'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# provide additional discount to the products
@admin.route('/product/additonal/discount', methods=['POST'])
def provide_discount():
    if 'id' in session:
        discount = request.form["offer"]

        pr_id = request.args.get('product_id')

        product = Products.query.filter_by(product_id=pr_id).first()

        product.offer = int(discount)

        items = Vendor_products.query.filter_by(product_id=pr_id).all()

        for i in items:
            i.offer = int(discount)

        try:
            db.session.commit()

            return redirect(url_for('Admin.show_products'))
        except Exception as e:
            print(e)
            db.session.rollback()

            return redirect(url_for('Admin.show_products'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove additional discount to the products
@admin.route('/product/additonal/discount/remove')
def remove_discount():
    if 'id' in session:
        pr_id = request.args.get('product_id')

        product = Products.query.filter_by(product_id=pr_id).first()

        product.offer = 0

        items = Vendor_products.query.filter_by(product_id=pr_id).all()

        for i in items:
            i.offer = 0

        try:
            db.session.commit()

            return redirect(url_for('Admin.show_products'))
        except Exception as e:
            print(e)
            db.session.rollback()

            return redirect(url_for('Admin.show_products'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view to send products to vendor
@admin.route('/vendor/products/all')
def show_products_for_vendor():
    title = "Products | Admin"
    if 'id' in session:
        vendor = request.args.get('vendor_id')
        product = Products.query.all()
        return render_template('admin/admin_send_products_vendor.html',
                               title=title,
                               products=product,
                               vendor=vendor)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# send products to the vendor
@admin.route('/vendor/products/new', methods=['POST'])
def send_vendor_products():
    if 'id' in session:

        data = request.get_json()

        output = []

        for i in range(0, len(data)):
            if i == 0:
                order_data = {}
                order_data["vendor_id"] = data[i]["vendor_id"]
            else:
                product_data = {}
                product_data["product_id"] = data[i]["product_id"]
                product_data["quantity"] = int(data[i]["quantity"])
                output.append(product_data)

        for y in range(0, len(output)):
            product = Products.query\
                .filter_by(product_id=output[y]["product_id"])\
                .first()

            send_product = Vendor_products(product_id=output[y]["product_id"],
                                           category=product.category_name,
                                           product_name=product.product_name,
                                           description=product.description,
                                           price=product.price,
                                           discount=product.discount,
                                           offer=product.offer,
                                           quantity_left=output[y]["quantity"],
                                           quantity_recieved=output[y]["quantity"],
                                           vendor_details=order_data["vendor_id"])

            db.session.add(send_product)

        try:
            db.session.commit()

            return jsonify({"success": "1", "message": "Products Sended"})
        except Exception as e:
            print(e)
            db.session.rollback()

            return jsonify({"success": "0", "message": "Products  Not Sended"})
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# remove products from vendor table
@admin.route('/vendor/products/remove')
def remove_products_vendor():
    if 'id' in session:
        if request.args:
            data = request.args

            products = Vendor_products.query\
                .filter_by(vendor_details=data["vendor_id"],
                           product_id=data["product_id"])\
                .first()

            try:
                db.session.delete(products)
                db.session.commit()

                flash("Vendor Product Deleted", "success")
                return redirect(url_for('Admin.get_vendor_product',
                                        vendor_id=data["vendor_id"]))
            except Exception as e:
                print(e)
                db.session.rollback()

                flash("Product Not Deleted", "danger")
                return redirect(url_for('Admin.get_vendor_product',
                                        vendor_id=data["vendor_id"]))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# send the complains to the vendor
@admin.route('/vendor/complaints', methods=['POST'])
def send_vendor_complain():
    if 'id' in session:

        data = request.args

        complaint = Complaints.query\
            .filter_by(complain_id=data["complain_id"]).first()

        ven = Vendor.query.filter_by(vendor_id=data["vendor_id"])

        complaint.send_vendor_status = True
        try:
            db.session.commit()

            message_title = "Complaint Received"
            message_body = f"A complaint has been received of order id: { complaint.order_id }, Complaint ID: { complaint.complain_id }"

            result = send_push_vendor(message_title,
                                      message_body,
                                      ven.device_id)

            flash("Complain sended to vendor", "success")
            return redirect(url_for('Admin.show_complains'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Error occured while sending, Please try again!", "warning")
            return redirect(url_for('Admin.show_complains'))
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# view city and charge
@admin.route('/city/charge/get')
def get_city_charge_view():
    if 'id' in session:
        title = "Add City | Admin"
        item = Cityandcharge.query.all()
        return render_template('admin/add_city_charge.html',
                               title=title,
                               item=item)
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# add city and charge
@admin.route('/city/charge/add', methods=["POST"])
def add_city_charge_view():
    if 'id' in session:
        city = request.form['city']
        charge = request.form['charge']

        item = Cityandcharge.query\
            .filter_by(city=city).first()
        if item:
            flash('City Already Present', "warning")
            return redirect(url_for('Admin.get_city_charge_view'))

        new = Cityandcharge(city=city.lower(),
                            delivery_charge=charge.lower())
        try:
            db.session.add(new)
            db.session.commit()

            flash("City Added Successfully!!", "success")
            return redirect(url_for('Admin.get_city_charge_view'))
        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Error occured, Please try again!", "warning")
            return redirect(url_for('Admin.get_city_charge_view'))

        return render_template('admin/add_city_charge.html')
    flash("You are not authorised", "danger")
    return redirect(url_for('Admin.log_in'))


# delete city and charge
@admin.route('/city/charge/remove')
def remove_city_charge_view():
    if request.args:
        city = request.args.get('city')

        item = Cityandcharge.query\
            .filter_by(city=city).first()

        try:
            db.session.delete(item)
            db.session.commit()

            flash("City Deleted Successfully!!", "success")
            return redirect(url_for('Admin.get_city_charge_view'))

        except Exception as e:
            print(e)
            db.session.rollback()

            flash("Error occured, Please try again!", "warning")
            return redirect(url_for('Admin.get_city_charge_view'))


# logout admin session
@admin.route('/logout')
def logout():
    session.pop("id")
    return redirect(url_for('Admin.log_in'))
