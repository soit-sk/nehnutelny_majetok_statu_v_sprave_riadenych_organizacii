#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This scraper scrapes the data from the Ministry of Finance of The 
Slovak Republic. It processes the PDF list of the real-estate
property of the state.

"""

# INITIAL DATA

site_url = 'https://www.finance.gov.sk/'    # main page
start_page = 'Default.aspx?CatID=4733'      # subpage url
header_row = 0                              # use row number N as headers
column_count_row = 1                        # use row number N as column indexes (optional)
ignore_rows = 2                             # ignore first N rows per page (must set explicitly, even if header is set, eg. N = 1 with headers)
column_count = 38
diff_vert = 3
diff_horiz = 6


cellmap = {
    66: 'ID',
    79: 'ID2',
    226: 'Zariadenie',
    378: 'Typ',
    406: 'Druh',
    475: 'Druh2',
    631: 'Inventárne číslo',
    684: 'Rok nadobudnutia a kraj',
    740: 'Názov okresu',
    794: 'Názov obce',
    867: 'Názov KÚ',
    925: 'Ulica',
    994: 'Číslo VL',
    1021: 'Spoluvl. podiel',
    1069: 'Výmera v m^2',
    1179: 'Parcelné číslo',
    1209: 'Kolaudácia a správca objektu',
    1323: 'Užívateľ objektu',
    1423: 'Obstarávacia cena v EUR',
    1459: 'Zostatková cena v EUR',

}

import scraperwiki
import urllib2
import lxml
import lxml.html
import sys
import re
import collections

def process_columns(row):
    """
    Column post-processing (accepts a row of results)
    The values are inconsistent across columns - values bleed to previous/next cells, this function
    attemps to create a list of consistent and usable values.
    """

    # specify a standard list of colums for every row in the final resultset    
    item = collections.OrderedDict()
    cols = 'id organizacia zariadenie typ druh_1 druh_2'.split(' ')

    for col in cols:
        item[col] = None
    
    # id, organizacia
    if re.match('^\d+$', row['ID']):
        item['id'] = int(row['ID'])
        item['organizacia'] = row.get('ID2', None)
    else:
        results = re.findall('^(\d+) (.*)$', row['ID'])
        if results:
            item['id'] = int(results[0][0])
            item['organizacia'] = results[0][1]
        else:
            return None
    # zariadenie
    item['zariadenie'] = row.get('Zariadenie', None)

    # typ
    item['typ'] = row.get('Typ', None)

    # druh
    item['druh_1'] = row.get('Druh', None)
    item['druh_2'] = row.get('Druh2', None)

    return item


html = scraperwiki.scrape(site_url + start_page)

# get all pdf links
root = lxml.html.fromstring(html)
pdf_urls = root.cssselect("li.pdf > a")

for pdf_url in pdf_urls:
    pdf_url_text = site_url + pdf_url.get('href')
    print pdf_url_text

    pdf_text = scraperwiki.scrape(pdf_url_text)
    data = scraperwiki.pdftoxml(pdf_text)

    tree = lxml.etree.fromstring(data)
    #tree = lxml.etree.parse('data.xml')

    missed_rows_global = 0
    for p, page in enumerate(tree.xpath('page')):
        print "processing page" + page.get('number')

        rows = {}
        xmlcells = page.xpath('text')
        lastrow = 0
        missed_rows = 0

        for xmlcell in xmlcells:
            top = int(xmlcell.get('top'))
            
            for dev in range(diff_vert+1):
                if top+dev in rows:
                    rows[top+dev].append(xmlcell)
                    break
                elif top-dev in rows:
                    rows[top-dev].append(xmlcell)
                    break
                else:
                    pass
            else:
                rows[top] = []
                rows[top].append(xmlcell)
       
        pagedata = []
        for key in sorted(rows.keys()):
            
            itemvalues = {}
            
            for column in rows[key]:
                
                left = int(column.get('left'))
                
                for dev in range(diff_horiz+1):
                    if left+dev in cellmap:
                        itemvalues[cellmap[left+dev]] = column.xpath('string()')
                    elif left-dev in cellmap:
                        itemvalues[cellmap[left-dev]] = column.xpath('string()')

            # we only want records with an ID
            id = itemvalues.get('ID', '')
            if re.match('^\d+ \D.*', id) or (re.match('^\d+$', id) and 'ID2' in itemvalues):
                itemvalues_processed = process_columns(itemvalues)
                if itemvalues_processed is not None:
                    pagedata.append(itemvalues_processed)
                else:
                    missed_rows += 1
            else:
                missed_rows += 1

        scraperwiki.sqlite.save(unique_keys=['id'],data=pagedata)
        print "Missed rows: %s" % missed_rows
        missed_rows_global += missed_rows

    print "Processed %s pages. Missed %s rows." % (p+1, missed_rows_global) 
