import os

import requests
from flask import Flask
from flask import json
from flask import render_template
from flask import request
from flask.views import MethodView
from flask import session, redirect, url_for, escape


CERYX_API_HOST = os.getenv('CERYX_API_HOST')
CERYX_WEB_PASS = os.getenv('CERYX_WEB_PASS')

app = Flask(__name__)
app.secret_key = 'Qdfwoiwojwngoiwuz789h309828j'

@app.route('/')
def home():
    """
    Return the home page (dashboard) of Ceryx Web.
    """
    if 'username' in session:
        username = session['username']
        if username == CERYX_WEB_PASS:
            return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))

    return '''
   <h1>input the security code :</h1>
   <form action = "" method = "post">
      <p><input type ="password" name ="username"/></p>
      <p><input type ="submit" value ="Login"/></p>
   </form>
   '''

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))

class RoutesListAPI(MethodView):
    endpoint = f'{CERYX_API_HOST}/api/routes'

    def get(self):
        """
        Return the list of all routes registered in Ceryx.
        """
        response = requests.get(self.endpoint)
        response.raise_for_status()
        route_list = response.json()
        return json.jsonify(route_list)

    def post(self):
        """
        Create a new route in Ceryx.
        """
        response = requests.post(self.endpoint, json=request.json)
        response.raise_for_status()
        route = response.json()
        return json.jsonify(**route)


class RoutesDetailAPI(MethodView):
    def delete(self, route_source):
        """
        Delete the route identified by the given route source in Ceryx.
        """
        url = f'{CERYX_API_HOST}/api/routes/{route_source}'
        response = requests.delete(url)
        response.raise_for_status()
        return json.jsonify(), 204

routes_list_view = RoutesListAPI.as_view('routes_list_view')
routes_detail_view = RoutesDetailAPI.as_view('routes_detail_view')

app.add_url_rule(
    '/api/routes/',
    view_func=routes_list_view,
    methods=['GET', 'POST'],
)

app.add_url_rule(
    '/api/routes/<route_source>/',
    view_func=routes_detail_view,
    methods=['DELETE'],
)
