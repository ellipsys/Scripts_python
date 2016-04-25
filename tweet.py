#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Necesitas tweepy 3.3.0
import tweepy, time, datetime, random

CONSUMER_KEY = "YOUR KEY HERE"
CONSUMER_SECRET="CONSUMER KEY HERE"
ACCESS_KEY="ACCESS KEY HERE"
ACCESS_SECRET="ACCESS SECRET KEY HERE"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

filename=open('tweet.txt','r')#tweet.txt es el contenido del tweet que sera publicado
first_line=filename.readlines()
filename.close()

for line in first_line:
     api.update_status(status=line)
     print line
     lines = open('tweet.txt').readlines()
     open('tweet.txt', 'w').writelines(lines[1:])
     number_random = random.randint(200, 1000)#
     timeTweet = number_random / 60
     print timeTweet
     time.sleep(number_random) 
