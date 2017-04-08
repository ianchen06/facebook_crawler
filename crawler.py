#!/usr/bin/env python
# coding: utf-8
"""
    fb_fans_crawler
    ~~~~~~~

    A high performance Facebook graph API crawler for fan pages and public groups.

    :copyright: (c) 2017 YingHao(Ian) Chen <ianchen06@gmail.com>
"""
import gevent
from gevent import monkey
monkey.patch_all()

import logging
import os
import argparse

import requests
import rethinkdb as r

parser = argparse.ArgumentParser(description='Facebook page/group crawler')
parser.add_argument('base_url', metavar='N', type=str, nargs='?',
                    help='a base url for facebook graph api')

args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

r.set_loop_type('gevent')

fbid = os.getenv("FB_ID")
access_token = os.getenv("FB_ACCESS_TOKEN")
base_url = args.base_url or "https://graph.facebook.com/v2.8/{fbid}/feed?fields=message,comments,likes,shares,created_time&access_token={access_token}".format(fbid=fbid, access_token=access_token)

def get_posts(url):
    """

    :param url: The url of FB graph API endpoint
    :type url: str
    :returns: list of gevent Futures
    :rtype: list 

    """
    logger.info("Crawling post %s"%url)
    res = get_link(url)
    jobs = []
    for post in res['data']:
        jobs.append(gevent.spawn(parse_post, post))
    next_url = res['paging'].get('next')
    if next_url:
        jobs.append(get_posts(next_url))
    return jobs

def get_field(url):
    """

    :param url: The url of FB graph API endpoint
    :type url: str

    """
    res = get_link(url)
    field_data = parse_field(res)

def get_link(url):
    """

    :param url: The url of FB graph API endpoint
    :type url: str
    :returns: Requests response
    :rtype: Response object
    
    """
    res = requests.get(url)
    if res.status_code > 399:
        logger.error("Request Error, url is %s, message is %s" % (url, res.text))
    return res.json()

def parse_post(post_data):
    """

    :param url: post dict from graph api
    :type url: dict
    :returns: post dict for RethinkDB
    :rtype: dict 

    """
    post_id = post_data['id']
    likes = post_data['likes']['data'] if post_data.get('likes') else []
    shares = post_data['shares']['count'] if post_data.get('shares') else 0
    comments = post_data['comments']['data'] if post_data.get('comments') else []
    message = post_data['message'] if post_data.get('message') else []
    created_time = post_data['created_time']
    data = dict(message=message, post_id=post_id, created_time=created_time, likes=likes, shares=shares, comments=comments)
    store_post(data)
    
    for field in ['likes', 'comments']:
        next_url = post_data[field]['paging'].get('next') if post_data.get(field) else None
        if next_url:
            gevent.spawn(get_field(next_url))
            
    return data

def parse_field(data):
    """

    :param url: field dict from graph api
    :type url: dict
    :returns: field dict for RethinkDB
    :rtype: dict 

    """
    previous_url = data['paging']['previous'].split('/')
    post_id = previous_url[4]
    field = previous_url[5].split('?')[0]
    payload = data['data']
    
    field_data = {"field": field,
                  "data": {"post_id": post_id,
                           field: payload}
                 }
    store_post_field(field_data)
    
    next_url = data['paging'].get('next')
    if next_url:
        gevent.spawn(get_field(next_url))
        
    return field_data

def store_post_field(field_data):
    """Merge or Insert field data into RethinkDB

    :param url: field dict for RethinkDB
    :type url: dict

    """
    conn = r.connect()
    res = (r.db('fans_page')
    .table('asus')
    .insert(field_data['data'], conflict=lambda _id, old_doc, new_doc: old_doc.merge({field_data['field']: old_doc[field_data['field']] + new_doc[field_data['field']]}))
    .run(conn))
    conn.close()

def store_post(post_data):
    """Stores post data into RethinkDB

    :param url: post dict for RethinkDB
    :type url: dict

    """
    conn = r.connect()
    res = r.db('fans_page').table('asus').insert(post_data, conflict='update').run(conn)
    conn.close()

if __name__ == '__main__':
    jobs = get_posts(base_url)
    gevent.wait(jobs)
