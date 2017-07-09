#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get


ignore = {'multicore', 'microcontroller', 'RISC', 'moon flights'}

def include(tag):

    for p in tag.parents:

        # ignores tags in the page's table of contents, navigation header, and footer
        if 'id' in p.attrs.keys() and ('toc' in p['id'] or 'mw-navigation' in p['id'] or 'footer' in p['id']):
            return False;

        # ignores links to external references and wikipedia categories
        if 'class' in p.attrs.keys() and ('references' in p['class'] or 'reference' in p['class'] or 'catlinks' in p['class']):
            return False;

    # ignores the 'See also' links
    if tag.parent and tag.parent.find_previous_sibling('h2') and 'See also' in tag.parent.find_previous_sibling('h2').text:
        return False;

    # ignores company names, such as Intel in "Intel's Core i5"
    if tag.next_sibling and tag.next_sibling.string.startswith('\''):
        return False;

    # ingores tags specified directly in the ignore list
    if tag.text in ignore:
        return False;

    return True;


def format(text):
    return text.replace(" architecture", "").replace(" Architecture", "")


baseUrl = 'https://en.wikipedia.org/wiki/List_of_CPU_architectures'

doc = get(baseUrl).text
soup = BeautifulSoup(doc, 'html.parser')
listItems = soup.select('li')

answers = set()

for i in listItems:

    if not include(i): continue

    links = i.select('a')

    for link in links:
        if include(link) and not format(link.getText()) in answers:
            answers.add(format(link.getText()))

for answer in sorted(answers):
    print(answer)

