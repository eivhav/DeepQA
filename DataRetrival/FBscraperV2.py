# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA
# Facebook scraper base from https://github.com/minimaxir/facebook-page-post-scraper


import urllib.request
import json
import datetime
import csv
import time
import codecs

page_id_list = ["telenornorge" , "telianorge", "talkmore.no"  , "chess.no", "onecallmobil", "djuicenorge"]
company_name_list = ["Telenor Norge", "Telia Norge", "Talkmore" , "Chess",   "OneCall", "djuice Norge"]

app_id = ''#DO NOT SHARE WITH ANYONE!
app_secret = ''#DO NOT SHARE WITH ANYONE!

access_token = app_id + "|" + app_secret

def request_until_succeed(url):
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL %s: %s" % (url, datetime.datetime.now()))
            print("Retrying.")

    return response.read().decode(response.headers.get_content_charset())


# Needed to write tricky unicode correctly to csv
def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 })

def getFacebookPageFeedData(page_id, access_token, num_statuses):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    base = "https://graph.facebook.com/v2.6"
    node = "/%s/feed" % page_id # feed for everything, posts for company posts.
    fields = "/?fields=message,link,created_time,type,name,id,from," + \
            "comments.limit(10).summary(true),shares,reactions" + \
            ".limit(10).summary(true)"
    parameters = "&limit=%s&access_token=%s" % (num_statuses, access_token)
    url = base + node + fields + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url))

    return data



def processFacebookPageFeedStatus(status, access_token, company_name):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else \
            unicode_normalize(status['message'])


    link_name = '' if 'name' not in status.keys() else \
            unicode_normalize(status['name'])

    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else \
            unicode_normalize(status['link'])

    from_name = '' if 'from' not in status.keys() else \
            status['from']['name']


    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
            status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + \
            datetime.timedelta(hours=-5) # EST
    status_published = status_published.strftime(
            '%Y-%m-%d %H:%M:%S') # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
            status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
            status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']


    if 'comments' not in status or 'data' not in status['comments']:
        reply = 0
    elif len(status['comments']['data']) > 0 and status['comments']['data'][0]['from']['name'].strip() == company_name:
        reply = status['comments']['data'][0]['message']
    else:
        reply = 0

    # Return a tuple of all processed data


    if len(link_name) > 2 or reply == 0 or status_type != 'status':
        return None


    items = str(status_published) + ";" + \
            str(status_message).replace('\n', '').replace(';', ':').replace('\r', '') + ";" +  \
            str(reply).replace('\n', '').replace(';', ':').replace('\r', '') + ";" +  \
            str(from_name)


    return items






def scrapeFacebookPageFeedStatus(page_id, company_name, access_token):
        file = open('%s_facebook_visitor_posts.csv' % page_id, 'w+')
        has_next_page = True
        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()

        print("Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime))

        statuses = getFacebookPageFeedData(page_id, access_token, 100)

        while has_next_page:
            for status in statuses['data']:

                line = processFacebookPageFeedStatus(status,access_token, company_name)
                if line != None:

                    file.write(line + '\n' + '\n')

                # output progress occasionally to make sure code is not
                # stalling
                num_processed += 1
                if num_processed % 100 == 0:
                    print("%s Statuses Processed: %s" % \
                        (num_processed, datetime.datetime.now()))

            # if there is no next page, we're done.
            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(
                                        statuses['paging']['next']))
            else:
                has_next_page = False


        print("\nDone!\n%s Statuses Processed in %s" % \
            (num_processed, datetime.datetime.now() - scrape_starttime))
        file.close()


scrapeFacebookPageFeedStatus(page_id_list[0], company_name_list[0], access_token)

