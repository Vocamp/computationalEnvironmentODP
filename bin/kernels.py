#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
from bs4.element import Tag


ignore = {'Lisp Machines, Inc.', 'Symbolics', 'Texas Instruments', 'Xerox'}

levels = {}
levels['Apple Inc.'] = {3}
levels['On S/360, S/370, and successor mainframes'] = {3}
levels['On other hardware platforms'] = {3}


def before(tag1, tag2, startTag):

    if len(tag1) == 0: return False;
    if len(tag2) == 0 :return True;

    tempTag = startTag

    while tempTag and tempTag.previous_sibling:
        tempTag = tempTag.previous_sibling
        if isinstance(tempTag, Tag):
            if tag1 in tempTag.getText():
                return True
            elif tag2 in tempTag.getText():
                return False

    return True


def includeLI(tag):

    for p in tag.parents:

        # ignores tags in the page's table of contents, navigation header, and footer
        if 'id' in p.attrs.keys() and ('toc' in p['id'] or 'mw-navigation' in p['id'] or 'footer' in p['id']):
            return False;

        # ignores links to external references and wikipedia categories
        if 'class' in p.attrs.keys() and ('references' in p['class'] or 'reference' in p['class'] or 'catlinks' in p['class']):
            return False;

        # ignores navigation links 
        if 'role' in p.attrs.keys() and 'navigation' in p['role']:
            return False;

    # ignores the 'See also' links
    if tag.parent and tag.parent.find_previous_sibling('h2') and 'See also' in tag.parent.find_previous_sibling('h2').text:
        return False;

    # ignores the external links
    if tag.parent and tag.parent.find_previous_sibling('h2') and 'External links' in tag.parent.find_previous_sibling('h2').text:
        return False;

    return True;


def includeA(tag):

    # ignores tags specified directly in the ignore list
    if tag.text in ignore:
        return False;

    # ignores links to external references and wikipedia categories
    p = tag.parent
    if p and 'class' in p.attrs.keys() and 'reference' in p['class']:
        return False;

    # this page displays operating systems at various levels of specificity,from kernel down to 
    # particular distributions in some cases. the script allows the user to specify the correct 
    # level(s) of each list to pull using the 'levels' dictionary defined abouve. the code below
    # insures that the tag is at an acceptable level. if the level is not specified, top-level
    # items are pulled.

    h4Depth = -1 # -1 because it takes one move to get out of the <a> tag itself 
    h4Heading = ''
    temp = tag
    while temp and not temp.find_previous_sibling('h4'):
        h4Depth += 1
        temp = temp.parent

    if temp and temp.find_previous_sibling('h4') and temp.find_previous_sibling('h4').select('span'):
            h4Heading = temp.find_previous_sibling('h4').select('span')[0].getText()

    h3Depth = -1 
    h3Heading = '' 
    temp = tag
    while temp and not temp.find_previous_sibling('h3'):
        h3Depth += 1
        temp = temp.parent

    if temp and temp.find_previous_sibling('h3') and temp.find_previous_sibling('h3').select('span'):
            h3Heading = temp.find_previous_sibling('h3').select('span')[0].getText()

    if h4Depth < h3Depth or before(h4Heading, h3Heading, temp) and h4Heading in levels:
        return h4Depth in levels[h4Heading]

    elif h3Heading in levels:
        return h3Depth in levels[h3Heading];

    else:
        return h3Depth == 1


baseUrl = 'https://en.wikipedia.org/wiki/List_of_operating_systems'

doc = get(baseUrl).text
soup = BeautifulSoup(doc, 'html.parser')
listItems = soup.select('li')

answers = set()

for i in listItems:

    if not includeLI(i): continue

    links = i.select('a')

    if links and includeA(links[0]) and not links[0].getText() in answers:
        answers.add(links[0].getText())

for answer in sorted(answers):
    print(answer)

