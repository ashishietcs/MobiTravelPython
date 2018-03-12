# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

from flask import Flask, jsonify, request
import flask_cors
from google.appengine.ext import ndb
import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()

app = Flask(__name__)
flask_cors.CORS(app)


# [START User]
class User(ndb.Model):
    """NDB model class for a user's User.

    Key is user id from decrypted token.
    """
    status = ndb.StringProperty()
    mobile_number = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty()
    address = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    otp = ndb.StringProperty()
# [END User]

# [START User]
class Ticket(ndb.Model):
    """NDB model class for a user's Ticket.
    Key is user id from decrypted token.
    """
    customer = ndb.KeyProperty(kind=User)
    from_loc = ndb.StringProperty(required=True)
    no_persons = ndb.IntegerProperty(required=True)
    to_loc = ndb.StringProperty(required=True)
    valid = ndb.BooleanProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
# [END User]


def convert_ticket_to_json(tickets):
    ticket_messages = []
    logging.info("No of ticekts "+str(len(tickets)))
    for ticket in tickets:
        ticket_messages.append({
            'id': ticket.key.urlsafe(),
            'from': ticket.from_loc,
            'to': ticket.to_loc,
            'persons': str(ticket.no_persons),
            'valid': str(ticket.valid),
            'created': ticket.created
        })
    logging.info("Ticket created "+str(ticket_messages))
    return ticket_messages
	
# [START query_database]
def query_tickets(user_id):
    """Fetches all Tickets associated with user_id.

    Users are ordered them by date created, with most recent User added
    first.
    """
    query = Ticket.query(Ticket.customer == user_id).order(-Ticket.created)
    notes = query.fetch()
    return convert_ticket_to_json(notes)
# [END query_database]


# [START query_database]
def query_users(mobile_id):
    """Fetches all Users associated with user_id.

    Users are ordered them by date created, with most recent User added
    first.
    """
    query = User.query(User.mobile_number==int(mobile_id)).order(-User.created)
    return query.fetch()
# [END query_database]

def convert_user_to_json(users):
    user_messages = []
    logging.info("No of users "+str(len(users)))
    for user in users:
        user_messages.append({
            'id': user.key.urlsafe(),
            'name': user.name,
            'status': user.status,
            'created': user.created
        })
    logging.info("User message created "+str(user_messages))
    return user_messages
	
# [START query_database]
def load_all_users():
    """Fetches all Users .
    Users are ordered them by date created, with most recent User added
    first.
    """
    query = User.query().order(-User.created)
    notes = query.fetch()
    return convert_user_to_json(notes)
# [END query_database]

# [START create_ticket]
@app.route('/user/<user_id>/ticket', methods=['POST','PUT'])
def create_ticket(user_id):
    """Returns a list of Tickets added by the current Firebase user."""
    user_key = ndb.Key(urlsafe=user_id)

    # [START create_entity]
    data = request.get_json()
    tkt = Ticket()
    tkt.no_persons = int(data['persons'])
    tkt.from_loc = data['from']
    tkt.to_loc = data['to'] 
    tkt.valid = True
    tkt.customer = user_key
    tkt_key = tkt.put()
    response = []
    response.append({
        'id': tkt_key.urlsafe(),
        'from': tkt.from_loc,
        'to':tkt.to_loc,
        'persons':str(tkt.no_persons),
        'valid':str(tkt.valid),
        'created': tkt.created
     })
    return jsonify(response)
# [END list_tickets]

def create_dummy_ticket(user_id):
    tkt = Ticket()
    tkt.no_persons = int(1)
    tkt.from_loc = 'dwarka'
    tkt.to_loc = 'gurgaon' 
    tkt.valid =  True
    tkt.customer = user_id
    tkt_key = tkt.put()

# [START list_tickets]
@app.route('/user/<user_id>/ticket', methods=['GET'])
def list_tickets(user_id):
    """Returns a list of Tickets added by the current Firebase user."""
    user_key = ndb.Key(urlsafe=user_id)
#    create_dummy_ticket(user_key)
    tickets = query_tickets(user_key)
    return jsonify(tickets)
# [END list_tickets]


# [START list_tickets]
@app.route('/user/<user_id>/otp', methods=['POST'])
def validate_tickets(user_id):
    """Returns a list of Tickets added by the current Firebase user."""
    user_key = ndb.Key(urlsafe=user_id)
    data = request.get_json()
    user = user_key.get()
    otp =  data['otp_number']
    if otp != None and otp == user.otp:
        user.status = 'Verified'
        user.put()
    response = []
    response.append({
        'id': user.key.urlsafe(),
        'name': user.name,
        'status': user.status,
        'created': user.created
        })
    return jsonify(response)
# [END list_tickets]


@app.route('/user/<user_id>', methods=['GET'])
def list_user(user_id):
    """Returns a list of notes added by the current Firebase user."""
    user_key = ndb.Key(urlsafe=user_id)
    logging.info("user id is " + user_id)
    user = user_key.get()
    logging.info("user details are "+str(user.mobile_number))
    response = []
    response.append({
        'id': user.key.urlsafe(),
        'name': user.name,
        'status': user.status,
        'created': user.created
        })
    return jsonify(response)

def create_dummy_user():
    user = User()
    user.mobile_number = 1234567890
    user.put()

def send_otp(mobile_number):
    return "1234"

# [START create_user]
@app.route('/user', methods=['POST', 'PUT'])
def create_user():

    # [START create_entity]
    data = request.get_json()
    users =  query_users(data['mobile_number'])
    if len(users) > 0:
        user = users[0]
    else:
        user = User()
        user.mobile_number = int(data['mobile_number'])
    if data['name'] != None:
        user.name = data['name']
    if data['address'] != None:
        user.address = data['address'] 
    user.status = 'unverified'
    user.otp = send_otp(user.mobile_number)
    user.put()
    response = []
    response.append({
        	'id': user.key.urlsafe(),
            'name': user.name,
            'status': user.status,
            'created': user.created
     })
    return jsonify(response)
# [END create_user]

# [START get_users]
@app.route('/user', methods=['GET'])
def get_users():
#    create_dummy_user()
    users = load_all_users()
    return jsonify(users)
#[END get_users]


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
# [END app]
