from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from web import db, app, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


# creating the admin table
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    prof_img = db.Column(db.String(20), nullable=False,
                         default='default.jpg')
    admin = db.Column(db.Boolean, default=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.admin_id}).decode('utf--8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            admin_id = s.loads(token)['user_id']
        except Exception as e:
            print(e)
            return None
        return Admin.query.filter_by(admin_id=admin_id).first()


# add city to database
class Cityandcharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(80), unique=True, nullable=False)
    delivery_charge = db.Column(db.Integer, nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    prof_img = db.Column(db.String(20), nullable=False,
                         default='default.jpg')
    items = db.relationship('Products',
                            cascade='all,delete',
                            backref='category',
                            lazy=True)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), unique=True, nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prof_img = db.Column(db.String(20), nullable=False,
                         default='default.jpg')
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    offer = db.Column(db.Integer, nullable=False, default=0)
    rate = db.relationship('Productratings',
                           cascade='all,delete',
                           backref='product',
                           lazy=True)
    category_name = db.Column(db.String(50),
                              db.ForeignKey('category.name'),
                              nullable=False)


class Productratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    product_details = db.Column(db.String(50),
                                db.ForeignKey('products.product_id'),
                                nullable=False)


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    store_name = db.Column(db.String(50), nullable=False)
    house_no = db.Column(db.Text, nullable=False)
    landmark = db.Column(db.Text, nullable=False)
    locality = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String(60), nullable=False,
                         default='00.00')
    longitude = db.Column(db.String(60), nullable=False,
                          default='00.00')
    device_id = db.Column(db.String(180), nullable=False,
                          default='key')
    vendor_status = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    prof_img = db.Column(db.String(20), nullable=False,
                         default='default.jpg')
    products = db.relationship('Vendor_products',
                               cascade='all,delete',
                               backref='vendor',
                               lazy=True)
    complaints = db.relationship('Complaints',
                                 cascade='all,delete',
                                 backref='vendor',
                                 lazy=True)
    new_orders = db.relationship('New_order',
                                 cascade='all,delete',
                                 backref='vendor',
                                 lazy=True)
    ongoing_orders = db.relationship('Ongoing_order',
                                     cascade='all,delete',
                                     backref='vendor',
                                     lazy=True)
    prev_orders = db.relationship('Prev_order',
                                  cascade='all,delete',
                                  backref='vendor',
                                  lazy=True)
    user_rating = db.relationship('Vendor_rating',
                                  cascade='all,delete',
                                  backref='vendor',
                                  lazy=True)
    delivery_boys = db.relationship('Deliveryboy',
                                    cascade='all,delete',
                                    backref='vendor',
                                    lazy=True)


class Vendor_products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    offer = db.Column(db.Integer, nullable=False)
    quantity_left = db.Column(db.Integer, nullable=False)
    quantity_recieved = db.Column(db.Integer, nullable=False)
    available_status = db.Column(db.Boolean, default=False)
    product_received_date = db.Column(db.DateTime, nullable=False,
                                      default=datetime.now)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class Complaints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complain_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complain_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    send_vendor_status = db.Column(db.Boolean, default=False)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class New_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    bill = db.Column(db.Integer, nullable=False)
    total_bill = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.now)
    delivery_method = db.Column(db.Text, nullable=False,
                                default='default')
    products = db.relationship('New_order_products',
                               cascade='all,delete',
                               backref='new_order',
                               lazy=True)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class New_order_products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    order = db.Column(db.String(50), db.ForeignKey('new_order.order_id'),
                      nullable=False)


class Ongoing_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_boy_id = db.Column(db.String(50), nullable=False)
    bill = db.Column(db.Integer, nullable=False)
    total_bill = db.Column(db.Integer, nullable=False)
    order_approve_date = db.Column(db.DateTime, nullable=False,
                                   default=datetime.now)
    delivery_method = db.Column(db.Text, nullable=False)
    pickup_status = db.Column(db.Boolean, default=False)
    products = db.relationship('Ongoing_order_products',
                               cascade='all,delete',
                               backref='ongoing_order',
                               lazy=True)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class Ongoing_order_products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    order = db.Column(db.String(50),
                      db.ForeignKey('ongoing_order.order_id'),
                      nullable=False)


class Prev_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_boy_id = db.Column(db.String(50), nullable=False)
    bill = db.Column(db.Integer, nullable=False)
    total_bill = db.Column(db.Integer, nullable=False)
    complete_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.now)
    delivery_method = db.Column(db.Text, nullable=False)
    products = db.relationship('Prev_order_products',
                               cascade='all,delete',
                               backref='complete_order',
                               lazy=True)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class Prev_order_products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    order = db.Column(db.String(50), db.ForeignKey('prev_order.order_id'),
                      nullable=False)


class Vendor_rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class Deliveryboy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), nullable=False)
    prof_img = db.Column(db.String(20), nullable=False,
                         default='default.jpg')
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    device_id = db.Column(db.String(180), nullable=False,
                          default='key')
    admin = db.Column(db.Boolean, default=False)
    vendor_details = db.Column(db.String(50),
                               db.ForeignKey('vendor.vendor_id'),
                               nullable=False)


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    contact_one = db.Column(db.String(20), nullable=False)
    contact_two = db.Column(db.String(20))
    admin = db.Column(db.Boolean, default=False)
    const_house_no = db.Column(db.Text, nullable=False)
    const_landmark = db.Column(db.Text, nullable=False)
    const_locality = db.Column(db.Text, nullable=False)
    const_city = db.Column(db.String(50), nullable=False)
    const_state = db.Column(db.Text, nullable=False)
    const_pincode = db.Column(db.Integer, nullable=False)
    delivery_house_no = db.Column(db.Text, nullable=False)
    delivery_landmark = db.Column(db.Text, nullable=False)
    delivery_locality = db.Column(db.Text, nullable=False)
    delivery_city = db.Column(db.String(50), nullable=False)
    delivery_state = db.Column(db.Text, nullable=False)
    delivery_pincode = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String(60), nullable=False,
                         default='00.00')
    longitude = db.Column(db.String(60), nullable=False,
                          default='00.00')
    device_id = db.Column(db.String(180), nullable=False,
                          default='key')
    cart_items = db.relationship('Cart',
                                 cascade='all,delete',
                                 backref='customer_cart',
                                 lazy=True)
    fav_items = db.relationship('Favourites',
                                cascade='all,delete',
                                backref='customer_fav',
                                lazy=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_details = db.Column(db.String(50),
                                 db.ForeignKey('customer.customer_id'),
                                 nullable=False)


class Favourites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(50), nullable=False)
    customer_details = db.Column(db.String(50),
                                 db.ForeignKey('customer.customer_id'),
                                 nullable=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Promotionalcodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount = db.Column(db.Integer, nullable=False)


class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)


class Privacypolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)


class Faq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)


class Bannerimages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_1 = db.Column(db.String(20), nullable=False,
                        default='default.jpg')
    image_2 = db.Column(db.String(20), nullable=False,
                        default='default.jpg')
    image_3 = db.Column(db.String(20), nullable=False,
                        default='default.jpg')
    image_4 = db.Column(db.String(20), nullable=False,
                        default='default.jpg')
    image_5 = db.Column(db.String(20), nullable=False,
                        default='default.jpg')
