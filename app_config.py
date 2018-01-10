# configuration for local host
#client_secrets_path = 'client_secrets.json'
#db_path = 'sqlite:///db/catalog.db'+'?check_same_thread=False'

# configuration for deployment on apache2 web server
client_secrets_path = '/var/www/html/nk-catalog/client_secrets.json'    
db_path = 'sqlite:////var/www/html/nk-catalog/db/catalog.db'+'?check_same_thread=False'