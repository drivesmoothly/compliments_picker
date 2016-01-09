#!/usr/bin/env python

print "hello", '\n'

import configparser
import re
from random import randint
import collections

config = configparser.ConfigParser()
config.read("team.ini")

team = re.split(", |,", config['default']['team'])
team_size = len(team)
picks_count = int(config['default']['picks-count'])
random_retries = 3

def print_result(pool, picks):
    results = []
    for by in range(0, team_size):
        reviewer = [team[by]]
        for to in pool:
            if to[1] == by:
                reviewer.append(team[to[0]])
        results.append(reviewer)
        
    sum_picks = 0
    for i in picks:
        sum_picks += i[1]
    print 'extra picks: ', sum_picks
    print '\n'
    
    if int(config['default']['print-results']) != 0:
        print '\n'.join([', '.join(x) for x in results])

    if int(config['default']['send-email']) == 0:
        print 'not emailing'
    else:
        print 'emailing...'
        email_results(results)
    
def email_results(results):
    for review in results:
        msg = ""
        msg += "Hi, " + review[0] + ', please review the following(s): \r\n'
        for i in range(1, len(review)):
            msg += review[i]
            msg += "\n"
        msg += '\n'
        send_email(review[0], 'Review Assignments', msg)
        #send_email('"crisan.marius@gmail.com" <marius.crisan@ro.neusoft.com>', 'Review Assignments', msg)
        
def send_email(to, subject, body):
    import smtplib
    import os
    
    gmail_user = os.environ['COMPLIMENTS_EMAIL_USER']
    gmail_pwd = os.environ['COMPLIMENTS_EMAIL_PWD']
    FROM = gmail_user
    TO = to if type(to) is list else [to]
    SUBJECT = subject
    TEXT = body
    
    # prepare the actual message
    headers = "\r\n".join(["from: " + FROM,
                           "subject: " + SUBJECT,
                           "to: " + ', '.join(TO),
                           "mime-version: 1.0",
                           "content-type: text/plain"])
    message = headers + "\r\n\r\n" + TEXT
    try:
        server = smtplib.SMTP("mailgate.ro.neusoft.com", 25)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"
    
def unassigned(pool, not_equal_to):
    count = 0;
    for i in pool:
        if (i[1] == -1) and (i[0] != not_equal_to):
            count += 1
    return count
    
def assigned(pool):
    return len(pool) - unassigned(pool, -2)
    
def find_nth_unassigned(pool, nth, not_equal_to):
    count = 0
    for i in range(0, len(pool)):
        if (pool[i][1] == -1) and (pool[i][0] != not_equal_to):
            if count == nth:
                return i
            else:
                count += 1
    return -1

def pick(pool, picks, stack_level):
    # check if we have tried too many times
    if picks[stack_level][1] >= (random_retries - 1):
        return False
        
    # find out how many possible values do we have left
    max_random = unassigned(pool, stack_level)
    if (max_random < picks_count):
        return False
    
    for i in range(0, picks_count):
        pick = randint(0, max_random - 1)
        pick = find_nth_unassigned(pool, pick, stack_level)
        if pick == -1:
            raise
        picks[stack_level][2 + i] = pick
        pool[pick][1] = stack_level
        max_random -= 1
    picks[stack_level][1] += 1
    return True
    
def is_valid(pool, picks, stack_level):
    # some of them can have the same value
    items = []
    item_indexes = picks[stack_level][2:2+picks_count]
    for index in item_indexes:
        items.append(pool[index][0])
    duplicates = [x for x, count in collections.Counter(items).items() if count > 1]
    result = (len(duplicates) == 0)
    return result
    
def is_solution(pool, picks, stack_level):
    result = (stack_level == (team_size - 1))
    return result
       
def remove_from_pool(pool, picks, stack_level):
    for i in range(2, len(picks[stack_level])):
        if picks[stack_level][i] != -1:
            pool[picks[stack_level][i]][1] = -1
    
def init(picks, stack_level):
    picks[stack_level][1] = -1
    for i in range(0, picks_count):
        picks[stack_level][2 + i] = -1

def find_solution(team, picks_count):
    # validations
    if (team_size < 3):
        print "It is obvious for teams smaller than 3"
        return

    # prepare the pool as a list of pairs [[a, b], [c, d] ...] where
    #   a, c are reviewed and b, d are reviewers
        
    pool = []
    for i in range(picks_count):
        pool.extend([[x, -1] for x in range(0, team_size)])
    
    # prepare the list of picks as a list of [[a, att, p1, p2, p3, ...], ...]
    #   where a is a reviewer, att is the number of attempts and p1, p2, p3 are picks for the reviewer
    picks = [[x, -1] for x in range(0, team_size)]
    for p in picks:
        p.extend([-1 for x in range(0, picks_count)])
    
    # start the randomizer
    stack_level = 0
    
    while (stack_level >= 0):
        while pick(pool, picks, stack_level):
            if is_valid(pool, picks, stack_level):
                if is_solution(pool, picks, stack_level):
                    print_result(pool, picks)
                    return
                else:
                    stack_level += 1
                    init(picks, stack_level)
            remove_from_pool(pool, picks, stack_level)
        #raw_input('press any key to continue')
        stack_level -= 1
        remove_from_pool(pool, picks, stack_level)
    
    print "no solution found", '\n'

find_solution(team, picks_count)