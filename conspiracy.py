"""
conspiracy.py

Conspiracy - automated web app hacking

"""

import argparse

# Instantiate the argument parser
parser = argparse.ArgumentParser(description='Conspiracy - automated web app hacking')

parser.add_argument('target', type=str, help='Overall target URL')
parser.add_argument('--hitlist', type=str, help='Optional path to text file of URLs to analyze')
args = parser.parse_args()

inscope_urls = {}    # (sub)domains in scope
hitlist = []         # optional individual urls to specially hit

requested_items = {} # keeps track of every unique request

print(args.target)
print(args.hitlist)

output = ''

# add the overall target to inscope_urls
inscope_urls[args.target] = True

# was hitlist flag specified?
if args.hitlist != None:
    pass
    # is the given path valid for a file?
    #     read it in as a text file
    #     break down by lines
    #     add each item to the hitlist
    #     also add root url to `inscope_urls` if not already in there

# for each item in hitlist
for item in hitlist:
    pass
    #     request it in headless chrome, proxied through burp suite
    #     wait for it to load
    #     (add some hooks and handles at this point for future functionality)
    #     close the tab or whatever

# for each item in `inscope_urls`
for inscope_url, _ in inscope_urls.items():
    pass
    #     scan with burp (maybe just crawl by default)
    #     run sslyze

# print out all findings for user
print(output)
