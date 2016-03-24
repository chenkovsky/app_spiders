
    scrapy runspider gplay.py -a apps=app_file -a info=true -a review=true
    #  info means crawling detail information about app, 
    # review means crawling review about app.

    
    scrapy runspider wandoujia.py -o app.json