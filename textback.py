import os
import urllib
import cgi
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from twilio import twiml
from twilio.rest import TwilioRestClient

import jinja2
import webapp2
import hashlib

from webapp2_extras import sessions

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'])


DEFAULT_USER_NUMBER = '1111111111'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.
def user_key(user_number=DEFAULT_USER_NUMBER):
	"""Constructs a Datastore key for a User entity with user_number."""
	return ndb.Key('User', user_number)


class Template(ndb.Model):
	title = ndb.StringProperty()
	text = ndb.StringProperty()
	isSelected = ndb.BooleanProperty()

class User(ndb.Model):
	"""Models a User in the database"""
	phone = ndb.StringProperty()
	password = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
	templates = ndb.StructuredProperty(Template, repeated=True)

DEFAULT_TEMPLATES = [
	Template(
		title='Meeting',
		text='In a meeting, text you in a bit.',
		isSelected=False),
	Template(
		title='Shower',
		text='In the shower, text you when I get out.',
		isSelected=False),
	Template(
		title='Lost',
		text='Lost my phone. Email/Facebook message me instead.',
		isSelected=False)
]

class BaseHandler(webapp2.RequestHandler):
	def dispatch(self):
		# Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		# Returns a session using the default cookie key.
		return self.session_store.get_session()

sessionHandler = BaseHandler()

class MainPage(BaseHandler):

	def get(self):
		#checks to see if user is already logged in. If so, skips the login page.
		currentUserPhone = str(self.session.get('phone'))
		if (currentUserPhone == None or currentUserPhone == 'None'):
			temp = JINJA_ENVIRONMENT.get_template('templates/index.html')
			self.response.write(temp.render())
			return
		user = User.query(ancestor=user_key(currentUserPhone)).get()

		selectedIndex = 0
		selectedTemplate = user.templates[0]
		for i in xrange(len(user.templates)):
			template = user.templates[i]
			if template.isSelected:
				selectedIndex = i
				selectedTemplate = template
		data = {
			'templates': user.templates,
			'currentTemplate': selectedTemplate,
			'currentTemplateIndex': selectedIndex
		}
		temp = JINJA_ENVIRONMENT.get_template('templates/home.html')
		self.response.write(temp.render(data))

	def post(self):
		return

class Login(BaseHandler):

	def post(self):
		phone = cgi.escape(self.request.get('phone')) #ensure that phone number is 10 digits with ONLY digits.
		password = cgi.escape(self.request.get('password'))
		hashedPhone = createHash(phone)
		user = User.query(ancestor=user_key(hashedPhone)).get()
		if user:
			self.response.write("phone: %s  password: %s" % (phone, password))
			self.session['phone'] = hashedPhone # store hashed value of current user's phone number.
			self.session['unhashed'] = phone
		self.redirect('/') #failed login. Have an alert or some user feedback.
		return

class Logout(BaseHandler):
	def get(self):
		self.session['phone'] = None
		self.session['unhashed'] = None
		self.redirect('/')
		return

class newUser(BaseHandler):
	def get(self):
		temp = JINJA_ENVIRONMENT.get_template('templates/register.html')
		self.response.write(temp.render())
		return

	def post(self):
		phone = cgi.escape(self.request.get('phone')) #ensure that phone number is 10 digits with ONLY digits.
		password = cgi.escape(self.request.get('password'))
		hashedPhone = createHash(phone)
		hashedPassword = createHash(password)
		user = User(phone=hashedPhone,
					password=hashedPassword,
					templates=DEFAULT_TEMPLATES,
					parent=user_key(hashedPhone))
		user.put()

		self.session['phone'] = hashedPhone
		self.session['unhashed'] = phone
		self.redirect('/')


def toJSON(t):
	d = {}
	d['isSelected'] = t.isSelected
	d['title'] = str(t.title)
	d['text'] = str(t.text)
	return d

class templateAndroid(BaseHandler):

	def post(self): #receive phone number and pin from Android. Respond with All templates.
		currentUserPhoneUnHashed = self.request.get('phone')
		currentUserPhone = createHash(currentUserPhoneUnHashed)
		user = User.query(ancestor=user_key(currentUserPhone)).get()
		self.response.write(json.dumps(map(toJSON, user.templates)))
		return

class templateCRUD(BaseHandler):

	# creating a new template
	def post(self):
		currentUserPhone = self.session.get('phone')
		user = User.query(ancestor=user_key(currentUserPhone)).get()
		newTitle = str(cgi.escape(self.request.get('title')))
		newText = str(cgi.escape(self.request.get('text')))
		user.templates.append(Template(title=newTitle, text=newText, isSelected=False))
		user.put()
		result = {
			'id': len(user.templates) - 1,
			'newTitle': newTitle
		}
		self.response.write(json.dumps(result))
		return


class singleTemplate(BaseHandler):

	def get(self, template_id): #return html for form editing a single template
		template_id = int(template_id)
		#checks to see if user is already logged in. If so, skips the login page.
		currentUserPhone = self.session.get('phone')
		if currentUserPhone == None:
			temp = JINJA_ENVIRONMENT.get_template('templates/index.html')
			self.response.write(temp.render())
			return
		user = User.query(ancestor=user_key(currentUserPhone)).get()
		if (template_id == -1):
			data = {
			'currentTemplate': {'title': "", 'text': ""},
			'currentTemplateIndex': template_id
			}
		else:
			data = {
			'currentTemplate': user.templates[template_id],
			'currentTemplateIndex': template_id
			}
		temp = JINJA_ENVIRONMENT.get_template('templates/editTemplateForm.html')
		self.response.write(temp.render(data))
		return

	def post(self, template_id): #allow editing of a single template in the server.
		template_id = int(template_id)
		currentUserPhone = self.session.get('phone')
		user = User.query(ancestor=user_key(currentUserPhone)).get()
		selectedTemplate = user.templates[template_id]
		selectedTemplate.title=cgi.escape(self.request.get('title'))
		selectedTemplate.text=cgi.escape(self.request.get('text'))
		changeSelected = str(cgi.escape(self.request.get('isSelected'))).capitalize()
		if changeSelected != '':
			for template in user.templates:
				template.isSelected=False
			if changeSelected == 'True':
				selectedTemplate.isSelected= True
			else:
				selectedTemplate.isSelected=False
		user.put()
		result = {
			'status': 'ok',
			'id': template_id,
			'newTitle': selectedTemplate.title
		}
		self.response.write(json.dumps(result))
		return

	def delete(self, template_id):
		template_id = int(template_id)
		currentUserPhone = self.session.get('phone')
		user = User.query(ancestor=user_key(currentUserPhone)).get()
		del user.templates[template_id]
		user.put()
		self.response.write(json.dumps({'status': 'ok', 'id': template_id}))

class SendSMS(BaseHandler):
	def post(self):
		text = cgi.escape(self.request.get('text'))
		phone = self.session.get('unhashed')
		# replace with your credentials from: https://www.twilio.com/user/account
		account_sid = "" # PLACE ACCOUNT_SID HERE
		auth_token = "" # PLACE AUTH_TOKEN HERE
		client = TwilioRestClient(account_sid, auth_token)
		rv = client.sms.messages.create(to="+1"+phone,
										from_="+14125676196",
										body=text)
		self.response.write(str(rv))

def createHash(string):
	return hashlib.sha256(string).hexdigest()

config = {}
config['webapp2_extras.sessions'] = {
	'secret_key': 'my-super-secret-key',
}

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/login', Login),
	('/logout', Logout),
	('/newUser', newUser),
	('/templates/android', templateAndroid),
	('/templates/new', templateCRUD),
	('/templates/(\d)', singleTemplate),
	('/send_sms', SendSMS),
], debug=True, config=config)
