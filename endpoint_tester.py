#!/usr/bin/env python

"""
Module "endpoint_tester" calls Catalog App API's to test the functionality.
"""
import httplib2
import sys
import json
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


print "Running Endpoint Tester....\n"
address = raw_input("""
Please enter the address of the server you want to access,
If left blank the connection will be set to 'http://localhost:8000':
""")
if address == '':
	address = 'http://localhost:8000'

# GET authorized user data and login :
# GET  '/api/resource'
user_id = 0
username = 'naci'
password = 'Udacity'


try:
    print('')
    print "Attempting Login......"
    url = address + '/api/resource'
    h = httplib2.Http()
    h.add_credentials(username, password)
    resp, result = h.request(url, method='GET')
    if resp['status'] != '200':
        raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
    print json.loads(result)
except Exception as err:
    print "Login FAILED: Could NOT login"
    print err.args
    sys.exit()
else:
    login_result = json.loads(result)
    user_id = login_result[0]['id']
    print('Login successfully with user %s' % login_result[2]['email'])


# TEST 1 -- CREATE NEW CATEGORY :
# POST  '/api/categories?name=Ironman'

try:
    print('')
    print "Attempting Test 1:Creating new Category......"
    url = address + '/api/categories?name=Ironman'
    h = httplib2.Http()
    h.add_credentials(username, password)
    resp, result = h.request(url, 'POST')
    if resp['status'] != '200':
        raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
    print json.loads(result)
    url = address + '/api/categories?name=TourDeFrance'
    h = httplib2.Http()
    h.add_credentials(username, password)
    resp, result = h.request(url, 'POST')
    if resp['status'] != '200':
        raise Exception("""Received an unsuccessful status code of
         %s""" % resp['status'])
    print json.loads(result)
except Exception as err:
    print "Test 1 FAILED: Could not add new category"
    print err.args
    sys.exit()
else:
    print "Test 1 PASS: Succesfully Made all new categories"

# TEST 2 -- READ ALL CATEGORIES :
# GET '/api/categories'

try:
    print('')
    print "Attempting Test 2: Reading all Categories..."
    url = address + "/api/categories"
    h = httplib2.Http()
    h.add_credentials(username, password)
    resp, result = h.request(url, 'GET')
    if resp['status'] != '200':
        raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
    all_result = json.loads(result)
    print result
except Exception as err:
    print "Test 2 FAILED: Could not retrieve categories from server"
    print err.args
    sys.exit()
else:
    print "Test 2 PASS: Succesfully read all categories"

# TEST 3 -- READ A SPECIFIC CATEGORY :
# GET /api/category/<int:id>

    try:
        print('')
        print "Attempting Test 3: Reading the last created category..."
        result = all_result
        catID = result['Category'][len(result['Category'])-1]['id']
        url = address + "/api/category/%s" % catID
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'GET')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
    except Exception as err:
        print "Test 3 FAILED: Could not retrieve category from server"
        print err.args
        sys.exit()
    else:
        print "Test 3 PASS: Succesfully read last category"

# TEST 4 -- UPDATE A SPECIFIC CATEGORY :
# PUT /api/category/<int:id>/?name=NameChanged

    try:
        print('')
        print "Attempting Test 4: Update the last created category name.."
        result = all_result
        catID = result['Category'][len(result['Category'])-1]['id']
        url = address + "/api/category/%s" % catID
        newName = 'TourDe-Udacity'
        url += '?name='
        url += newName
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'PUT')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
    except Exception as err:
        print "Test 4 FAILED: Could not update category name "
        print err.args
        sys.exit()
    else:
        print ("""
Test 4 PASS: Succesfully updated last category name to : %s""" % newName)

# TEST 5 -- DELETE A SPECIFIC CATEGORY :
# DELETE /api/category/<int:id>

    try:
        print('')
        print "Attempting Test 5: DELETE the last changed  category .."
        result = all_result
        catID = result['Category'][len(result['Category'])-1]['id']
        url = address + "/api/category/%s" % catID
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'DELETE')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
    except Exception as err:
        print "Test 5 FAILED: Could not delete category  "
        print err.args
        sys.exit()
    else:
        print ("""
Test 5 PASS: Succesfully deleted last category with ID = %s""" % catID)

# TEST 6 -- CREATE NEW CATEGORY ITEM :
# GET  '/api/category/<int:id>/items'

    try:
        print('')
        print "Attempting Test 6:Creating new Category Item......"
        result = all_result
        catID = result['Category'][len(result['Category'])-2]['id']
        urlCategory = address + "/api/category/%s" % catID
        url = urlCategory + '/items?title=Neopren&description=needed'
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'POST')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
        url = urlCategory + '/items?title=Cycle&description=For180Km'
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'POST')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
    except Exception as err:
        print "Test 6 FAILED: Could not add new category item"
        print err.args
        sys.exit()
    else:
        print ("""
Test 6 PASS: Succesfully creatd 2 new items to
last category with ID = %s""" % catID)

# TEST 7 -- READ ALL CATEGORY ITEMS:
# GET  '/api/category/<int:id>/items'

    try:
        print('')
        print "Attempting Test 7:Read all items for  Category with ID=10......"
        result = all_result
        catID = result['Category'][len(result['Category'])-2]['id']
        urlCategory = address + "/api/category/%s" % catID
        url = urlCategory + '/items'
        h = httplib2.Http()
        h.add_credentials(username, password)
        resp, result = h.request(url, 'GET')
        if resp['status'] != '200':
            raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
        print json.loads(result)
        all_items = json.loads(result)
    except Exception as err:
        print "Test 7 FAILED: Could not read all category items"
        print err.args
        sys.exit()
    else:
        print ("""
Test 7 PASS: Succesfully read all items to
last category with ID = %s""" % catID)
        try:
            print('')
            print "Attempting Test 8:Update an item"
            result = all_result
            catID = result['Category'][len(result['Category'])-2]['id']
            resultItems = all_items
            itemID = all_items['Items'][0]['id']
            urlCategory = address + "/api/category/%s" % catID
            url = urlCategory + '/items/%s' % itemID
            url += '?title=Patrick+Lange&description=from+Darmstadt'
            h = httplib2.Http()
            h.add_credentials(username, password)
            resp, result = h.request(url, 'PUT')
            if resp['status'] != '200':
                raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
            print json.loads(result)
        except Exception as err:
            print "Test 8 FAILED: Could not update item"
            print err.args
            sys.exit()
        else:
            print ("""
Test 8 PASS: Succesfully updated title and description for item
last category with ID = %s""" % catID)
        try:
            print('')
            print "Attempting Test 9:Delete an item"
            result = all_result
            catID = result['Category'][len(result['Category'])-2]['id']
            resultItems = all_items
            itemID = all_items['Items'][1]['id']
            urlCategory = address + "/api/category/%s" % catID
            url = urlCategory + '/items/%s' % itemID
            h = httplib2.Http()
            h.add_credentials(username, password)
            resp, result = h.request(url, 'DELETE')
            if resp['status'] != '200':
                raise Exception("""
Received an unsuccessful status code of %s""" % resp['status'])
            print json.loads(result)
        except Exception as err:
            print "Test 9 FAILED: Could not delete item"
            print err.args
            sys.exit()
        else:
            print ("""
Test 9 PASS: Succesfully deleted item with ID = %s""" % itemID)
