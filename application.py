from flask import Flask, render_template, jsonify, url_for, redirect, flash
import requests, json
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


import config

application = Flask(__name__)

application.config['SECRET_KEY'] = config.secretkey #'secret'



#add validators to see if the string is a valid email address
# / valid Stellar address

#The below are FlaskForm objects imported from "WTForms":
#https://wtforms.readthedocs.io/en/stable/
#brought in through the "Flask-WTF" package:
#http://flask-wtf.readthedocs.io/en/stable/

#Currently, the only validator being used is "DataRequired()", which
#simply checks if any data was put in the field.

#TODO: add other native and custom validators --
#https://wtforms.readthedocs.io/en/stable/validators.html#built-in-validators
# -- to check
# - is the stellar address a valid stellar address?
# - is the email address a valid email address?
# - is the code possibly a valid code?
# and include appropriate error messages for when these things fail.


#FORMS

class RegisterForm(FlaskForm):
	saddress = StringField('Stellar address', validators=[DataRequired()])
	eaddress = StringField('email address', validators=[DataRequired()])
	submit = SubmitField('register address')

class VerificationForm(FlaskForm):
	saddress = StringField('Stellar address', validators=[DataRequired()])
	ecode = StringField('4 digit code', validators=[DataRequired()])
	submit = SubmitField('register address')

class BountyForm(FlaskForm):
	saddress = StringField('Stellar address', validators=[DataRequired()])
	description = StringField('What needs to be done here?', validators=[DataRequired()])
	amount = IntegerField('Bounty Amount', validators=[DataRequired()])
	timeout = IntegerField('Days to expiration', validators=[DataRequired()])
	maxsub = IntegerField('Max # of submissions', validators=[DataRequired()])
	submit = SubmitField('post bounty')



#ROUTES ROUTES ROUTES

#TODO: homepage
@application.route("/", methods=['GET', 'POST'])
def home():
	form = BountyForm()

	if form.validate_on_submit(): 

		vdata = {'address': form.saddress.data}
		vrl = "http://localhost:5000/check"
		vr = requests.post(vrl, json=vdata) 
		vmessage = vr.json()['message']

		if vmessage == 'unverified':
			vmessage = 'error! address not registered.'
			flash(vmessage)
			return redirect(url_for('register'))
		
		data = {'address': form.saddress.data,
		'description': form.description.data,
		'amount': form.amount.data,
		'timeout': form.timeout.data,
		'maxsub': form.maxsub.data
		}
		url = "http://localhost:5000/bounty"
		r = requests.post(url, json=data) 
		message = r.json()['message']

		if message == 'error':
			message = 'there was an error.'
			flash(message)
			return redirect(url_for('home'))
		if message == 'success':
			message = 'Success!'
			flash(message)
		return redirect(url_for('home'))
	return render_template('complete.html', form=form)


#loads form, renders the form in a template
#when the user submits the data, it is sent to Registry
#TODO: errors from WTF-forms, errors from Registry

@application.route("/register", methods=['GET', 'POST'])
def register():
	form = RegisterForm()

	if form.validate_on_submit(): 
		data = {'address': form.saddress.data,'email': form.eaddress.data}
		url = "http://localhost:5000/register"
		r = requests.post(url, json=data) 
		message = r.json()['message']

		if message == 'error':
			message = 'error! address already in use.'
			flash(message)
			return redirect(url_for('register'))
		if message == 'address registered':
			message = 'Success!'
			flash(message)
		return redirect(url_for('verify'))
		
	return render_template('register.html', form=form)

#todo: need the registry to send json messages with a binary value
# "Success" or "Failure"
# Keep the error message content here on the front-end...

#then, here, need to separate the two cases:
# - success means render the next step template, flash green message
# - failure means render the same step template, flash red message



#TODO: ditto
@application.route("/verify", methods=['GET', 'POST'])
def verify():
	form = VerificationForm()
	if form.validate_on_submit():
		data = {'address': form.saddress.data,'code': form.ecode.data}
		url = "http://localhost:5000/verify"
		r = requests.post(url, json=data) 
		message = r.json()['message']
		if message == 'error':
			message = 'error! address/code invalid.'
			flash(message)
			return redirect(url_for('register'))
		if message == 'address verified':
			message = 'Success!'
			flash(message)
			return redirect(url_for('home'))
		flash(message)
	return render_template('verify.html', form=form)


@application.route("/board", methods=['GET', 'POST'])
def list():
	return "list"

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host='0.0.0.0', port=80)


