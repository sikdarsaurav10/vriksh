

class Config:

    SECRET_KEY = "b'\xb6\x08\x86\xe4\x13y\x9e\x11?\xe0\x80f7-^\x07'"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/organic'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'noreply@demo.com'
    MAIL_PASSWORD = 'password'
    MAP_SERVER_KEY = 'MAP_MY_INDIA SERVER API KEY'
    PUSH_API_KEY_CUSTOMER = 'FIREBASE_API_KEY FOR CUSTOMER APP'
    PUSH_API_KEY_VENDOR = 'FIREBASE_API_KEY FOR VENDOR APP'
    PUSH_API_KEY_DRIVER = 'FIREBASE_API_KEY FOR DELIVERY BOY APP'
    CLIENT_ID = 'MAP_MY_INDIA AUTH API KEY'
    CLIENT_SECRET = 'MAP_MY_INDIA AUTH API KEY'