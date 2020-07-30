from django.shortcuts import render
from django.http import HttpResponse

from run_search import amazonBot
#from order_data import table


def index(request):
    return render(request, 'index.html')


def search_result(request):
    item = request.POST

    # Instantiate AmazonBot class
    amazon_bot = amazonBot(item['searchItem'])
    prods = amazon_bot.search_items()
    amazon_bot.close_session()

    return render(request, 'index.html', {'prods': prods})
