import sys

#Expand Python classes path with your app's path
sys.path.insert(0, '/var/www/html/nk-catalog')

from controllers import app as application
from model_catalog import secret_key

#Initialize WSGI app object
application.secret_key = secret_key
application.debug = False
