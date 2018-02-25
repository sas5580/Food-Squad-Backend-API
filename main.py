from copy import deepcopy
from collections import defaultdict

from flask import Flask

from data import *


app = Flask(__name__)
data = init_data()
cuisines_type = get_cuisines(data)


USER_DATA = {}

def init_user(user):
	USER_DATA[user] = {
		'prefs': {'cuisines': defaultdict(int), 'prices': defaultdict(int)},
		'category': None,
		'price_range': None,
		'session': None
	}


@app.route('/l(ogin/<user>', methods=['GET'])
def login(user):
	message = 'logged in'
	status_code = 201

	try:
		if user not in USER_DATA.keys():
			init_user(user)
	except Exception as e:
		message = 'Error logging in: {}'.format(str(e))
		status_code = 500

	return ({'message': message}, status_code)


@app.route('/category/<user>/<category>', methods=['GET'])
def category(user, category):
	message = 'category selected'
	status_code = 200

	try:
		if user not in USER_DATA.keys():
			raise KeyError('Invalid user ' + category + '. Please login first')
		if category not in data.keys():
			raise KeyError('Invalid category ' + category)

		USER_DATA[user]['category'] = category
	except Exception as e:
		message = 'Error setting category: {}'.format(str(e))
		status_code = 500

	return_dict = {'message': message}
	if status_code == 200:
		return_dict.update({'cuisines': cuisines_type[category]})

	return (return_dict, status_code)


@app.route('/price/<user>/<min_>/<max_>', methods=['GET'])
def price(user, min_, max_):
	message = 'price range set and data formatted'
	status_code = 200

	try:
		if user not in USER_DATA.keys():
			raise KeyError('Invalid user ' + category + '. Please login first')

		USER_DATA[user]['price_range'] = (min_, max_)
	except Exception as e:
		message = 'Error setting price: {}'.format(str(e))
		status_code = 500

	try:
		category = USER_DATA[user]['category']
		price_range = USER_DATA[user]['price_range']
		USER_DATA[user]['session'] = format_data(data[category], price_range)
	except Exception as e:
		message = 'Error formatting data: {}'.format(str(e))
		status_code = 500

	return ({'message': message, 'question': get_best_restaurant(USER_DATA[user]['session'])}, status_code)

@app.route('/answer/<user>/<answer>', methods=['GET'])
def answer(user, answer):
	message = 'question answered'
	status_code = 200

	return_dict = {}

	try:
		if user not in USER_DATA.keys():
			raise KeyError('Invalid user ' + category + '. Please login first')
		if answer.lower() == 'yes':
			update_prefs(USER_DATA[user])
			return_dict = {
				'status': 'done',
				'recommendations': get_recommendations(USER_DATA[user]['session'], USER_DATA[user]['price_range']) 
			}
		else:
			update_session(USER_DATA[user]['session'], USER_DATA[user]['price_range'])
			return_dict = {
				'status': 'question',
				'question': get_best_restaurant(USER_DATA[user]['session'])
			}
	except Exception as e:
		message = 'Error answering question: {}'.format(str(e))
		status_code = 500

	return_dict.update({'message': message})

	return (return_dict, status_code)

if __name__ == '__main__':
  app.run(debug=True)
