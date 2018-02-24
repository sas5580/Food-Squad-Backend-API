import json
import random

DEFAULT_LOCATION = (43.6532, -79.3832)

CUSINESS_PENALTY = 3
PRICE_PENALTY = 1

PRICE_RANGE = (40, 70)

def get_price_level(p):
	delta = PRICE_RANGE[1] - PRICE_RANGE[0]
	return int((p-PRICE_RANGE[0]) / (delta/5.0))

CATEGORY = 'breakfast'

def get_data():
	data = {}
	with open('data/{}.json'.format(CATEGORY), 'r') as f:
		data = json.load(f)
	return data

def print_rest(rest):
	print(rest['name'])
	print('Cuisines: ', ', '.join(rest['cuisines']))
	print('Average Price: ', rest['price'])
	print()

def ask_rest(rest):
	print_rest(rest)
	return input('[yes/no]: ') == 'yes'


if __name__ == '__main__':
	data = get_data()
	rests = []
	for restaurant in data['restaurants']:
		price = float(restaurant['restaurant']['average_cost_for_two'])/2.0
		if PRICE_RANGE[0] <= price <= PRICE_RANGE[1]:
			rests.append({
				'name': restaurant['restaurant']['name'],
				'cuisines': restaurant['restaurant']['cuisines'].split(', '),
				'price_range': get_price_level(price),
				'price': price,
				'rating': float(restaurant['restaurant']['user_rating']['aggregate_rating']),
				'score': 0
			})

	rests.sort(key=lambda x: x['rating'], reverse=True)

	while True:
		rest = rests[0]
		res = ask_rest(rest)

		cs = rest['cuisines']
		p_r = rest['price_range']

		if res:
			rests.remove(rest)
			for r in rests:
				r['score'] = len(set(cs).intersection(r['cuisines'])) * CUSINESS_PENALTY
				if p_r == r['price_range']:
					r['score'] += PRICE_PENALTY

			rests.sort(key=lambda x: (x['score'], x['rating']), reverse=True)	

			print_rest(rest)
			for i in range(4):
				print_rest(rests[i])

			break

		for r in rests:
			r['score'] -= len(set(cs).intersection(r['cuisines'])) * CUSINESS_PENALTY
			if p_r == r['price_range']:
				r['score'] -= PRICE_PENALTY

		rests.sort(key=lambda x: (x['score'], x['rating']), reverse=True)
		for i in rests:
			print(i['name'], ' ', i['score'])
		print()