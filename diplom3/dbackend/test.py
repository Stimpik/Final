from pprint import pprint

from yaml import Loader, load

with open('data.yaml', encoding='utf-8') as f:
    read_data = load(f, Loader=Loader)
    for item in read_data.get('shop'):
        name = item['name']
        url = item['url']
        status = item['status']
    for category in read_data['categories']:
        id = category['id']
        name = category['name']
        print(id, name)

    for item in read_data['goods']:

        name = item['model']
        price = item['price']
        price_rrc = item['price_rrc']
        quantity = item['quantity']
        # print( name,price,price_rrc,quantity )
        pprint(item)
