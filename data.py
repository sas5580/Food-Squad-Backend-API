import json

CUSINESS_VALUE = 2	
PRICE_VALUE = 1

def get_price_level(p, price_range):
	delta = price_range[1] - price_range[0]
	return int((p-price_range[0]) / (delta/5.0))

DATA_TYPES = ['breakfast', 'cafes', 'dinner', 'drinks', 'lunch']

def init_data():
	data = {}
	for data_type in DATA_TYPES:
		with open('data/{}.json'.format(data_type), 'r') as f:
			data[data_type] = json.load(f)['restaurants']

	return data

def get_cuisines(restaurants_dict):
	data = {}
	for type_, restaurants in restaurants_dict.items():
		cuisines = set()
		for rest in restaurants:
			cuisines |= set(rest['restaurant']['cuisines'].split(', '))
		data[type_] = list(cuisines)
	return data

def calculate_score(cuisines, price_level, prefs, price_range):
	score = 0
	for cuisine_pref, amt in prefs['cuisines'].items():
		if cuisine_pref in cuisines:
			score += amt * CUSINESS_VALUE

	for price_pref, amt in prefs['prices'].items():
		if get_price_level(price_pref, price_range) == price_level:
			score += amt * PRICE_VALUE

	return score
 
def format_data(restaurants, price_range, prefs):
	fomratted_data = []
	for restaurant in restaurants:
		price = float(restaurant['restaurant']['average_cost_for_two'])/2.0
		if price_range[0] <= price <= price_range[1] and restaurant['restaurant']['thumb']:
			cuisines = set(restaurant['restaurant']['cuisines'].split(', '))
			price_level = get_price_level(price, price_range),
			score = calculate_score(cuisines, price_level, prefs, price_range)

			fomratted_data.append({
				'name': restaurant['restaurant']['name'],
				'cuisines': cuisines,
				'price_level': price_level,
				'price': price,
				'logo_url': restaurant['restaurant']['thumb'],
				'rating': float(restaurant['restaurant']['user_rating']['aggregate_rating']),
				'score': score
			})
	return fomratted_data

def get_best_restaurant(restaurants):
	restaurants.sort(key=lambda x: (x['score'], x['rating']), reverse=True)
	return restaurants[0]

def get_recommendations(session):
	price_range = session['price_range']
	cuisines = session['session'][0]['cuisines']
	price_level = get_price_level(session['session'][0]['price'], price_range)
	data = [session['session'].pop(0)]
	for r in session['session']:
		r['score'] = len(cuisines.intersection(r['cuisines'])) * CUSINESS_VALUE
		if price_level == r['price_level']:
			r['score'] += PRICE_VALUE

	session['session'].sort(key=lambda x: (x['score'], x['rating']), reverse=True)	

	for i in range(4):
		data.append(session['session'][i])

	return data

def update_session(session):
	price_range = session['price_range']
	cuisines = session['session'][0]['cuisines']
	price_level = get_price_level(session['session'][0]['price'], price_range)
	for r in session['session']:
		r['score'] -= len(cuisines.intersection(r['cuisines'])) * CUSINESS_VALUE
		if price_level == r['price_level']:
			r['score'] -= PRICE_VALUE

def update_prefs(session):
	liked_cuisines = session['session'][0]['cuisines']
	liked_price = session['session'][0]['price']

	for cuisine in liked_cuisines:
		session['prefs']['cuisines'][cuisine] += 1
	session['prefs']['prices'][liked_price] += 1

	disliked_cuisines = session['session'][-1]['cuisines']
	disliked_price = session['session'][-1]['price']

	for cuisine in disliked_cuisines:
		session['prefs']['cuisines'][cuisine] -= 1
	session['prefs']['prices'][disliked_price] -= 1