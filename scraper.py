#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This scraper scrapes the data from the Ministry of Finance of The 
Slovak Republic. It processes the list of the real-estate
property of the state.

This is a new and updated version - since they began publishing
the list in XML format.
"""

# INITIAL DATA

site_url = 'https://www.finance.gov.sk/'    # main page
start_page = 'Default.aspx?CatID=4733'      # subpage url
DEBUG = False

import scraperwiki
import urllib2
import lxml
import lxml.html
import sys
import re
import collections

import mydebug as d
d.DEBUG = DEBUG # enable for debug output
from mydebug import prt

if not DEBUG:
    html = scraperwiki.scrape(site_url + start_page)

    # get all pdf links
    root = lxml.html.fromstring(html)
    xml_urls = root.cssselect("li.xml > a")
else:
    xml_urls = [{'href': 'dummy_URL'}]


# cellmap
cellmap = collections.OrderedDict([
    ('id', {'column': 0, 'type': 'Number'}),
    ('organizacia', {'column': 1, 'type': 'String'}),
    ('zariadenie', {'column': 2, 'type': 'String'}),
    ('druh_nehnutelnosti_1', {'column': 4, 'type': 'String'}),
    ('druh_nehnutelnosti_2', {'column': 5, 'type': 'String'}),
    ('inventarne_cislo', {'column': 6 }),
    ('rok_nadobudnutia', {'column': 7 }),
    ('kraj', {'column': 8 }),
    ('okres', {'column': 9 }),
    ('obec', {'column': 10 }),
    ('krajsky_urad', {'column': 11 }),
    ('adresa_objektu', {'column': 12 }),
    ('c_listu_vlastnictva', {'column': 13 }),
    ('spoluvlastnicky_podiel', {'column': 14 }),
    ('vymera', {'column': 15 }),
    ('parcelne_cislo', {'column': 16 }),
    ('supisne_cislo', {'column': 17 }),
    ('datum_kolaudacie', {'column': 18 }),
    ('spravca_objektu', {'column': 19 }),
    ('uzivatel_objektu', {'column': 20 }),
    ('vstupna_obstaravacia_cena_v_EUR', {'column': 21 }),
    ('zostatkova_cena_v_EUR', {'column': 22 }),
    ('poznamka', {'column': 23 }),
])

# namespaces

ns = {
    'd': 'urn:schemas-microsoft-com:office:spreadsheet',
    'o': 'urn:schemas-microsoft-com:office:office',
    'x': 'urn:schemas-microsoft-com:office:excel',
    'ss': 'urn:schemas-microsoft-com:office:spreadsheet'
}


for filenum, xml_url in enumerate(xml_urls):
    xml_url_text = site_url + xml_url.get('href')
    prt(xml_url_text)

    if not DEBUG:
        xml_text = scraperwiki.scrape(xml_url_text)
        tree = lxml.etree.fromstring(xml_text)
    else:
        tree = lxml.etree.parse('kapitola_majetok_k_300.2015.xml')

    for t, table in enumerate(tree.xpath('//ss:Table', namespaces=ns)):
        prt('Processing table %s' % t)
        table_data = []

        for r, row in enumerate(table.xpath('ss:Row', namespaces=ns)):
            cells = row.xpath('ss:Cell', namespaces=ns)

            # do not even bother with rows shorter than 10 cells
            if len(cells) < 10:
                continue

            # initialize item
            item = collections.OrderedDict()

            # populate item (use static column addresses from the cellmap dict for mapping)
            for (variable, defs) in cellmap.items():
                if len(cells) > defs['column']:
                    if 'type' in defs:
                        res = cells[defs['column']].xpath('ss:Data[@ss:Type=\'' + defs['type'] + '\']/text()', namespaces=ns)
                    else:
                        res = cells[defs['column']].xpath('ss:Data/text()', namespaces=ns)

                    if res:
                        item[variable] = res[0]
                    else:
                        item[variable] = None
                else:
                    item[variable] = None

            if item['id'] is not None and item['organizacia'] is not None:
                table_data.append(item)

        scraperwiki.sqlite.save(unique_keys=['id'],data=table_data)













exit()


header_row = 0                              # use row number N as headers
column_count_row = 1                        # use row number N as column indexes (optional)
ignore_rows = 2                             # ignore first N rows per page (must set explicitly, even if header is set, eg. N = 1 with headers)
column_count = 38

# fine tuning - the positions will not be exact, look vert/horiz pixels around to the 
# boundary of nearest row/column

diff_vert = 4
diff_horiz = 7

# static column definitions
# NEW VALUES VALID FROM 2014-10-25
cellmap = {
    116: 'ID',
    148: 'ID2',
    543: 'Zariadenie',
    951: 'Typ',
    1024: 'Druh',
    1210: 'Druh2',
    1652: 'Inventárne číslo',
    1797: 'Rok nadobudnutia a kraj',
    1943: 'Názov okresu',
    2089: 'Názov obce',
    2285: 'Názov KÚ',
    2442: 'Ulica',
    2626: 'Číslo VL',
    2698: 'Spoluvl. podiel',
    2831: 'Výmera v m^2',
    2847: 'Výmera v m^2',
    3126: 'Parcelné číslo',
    3207: 'Kolaudácia a správca objektu',
    3337: 'Správca objektu',
    3239: 'Správca objektu',
    3510: 'Užívateľ objektu',
    3788: 'Obstarávacia cena v EUR',
    3800: 'Obstarávacia cena v EUR',
    3807: 'Obstarávacia cena v EUR',
    3884: 'Zostatková cena v EUR',
    3896: 'Zostatková cena v EUR',
    3913: 'Zostatková cena v EUR',

}

# THESE VALUES USED TO BE VALID
"""
cellmap = {
    116: 'ID',
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
    1222: 'Správca objektu',
    1323: 'Užívateľ objektu',
    1423: 'Obstarávacia cena v EUR',
    1459: 'Zostatková cena v EUR',

}
"""



def process_columns(row):
    """
    Column post-processing (accepts a row of results)
    The values are inconsistent across columns - values bleed to previous/next cells, this function
    attemps to create a list of consistent and usable values.
    """
    # specify a standard list of colums for every row in the final resultset    
    item = collections.OrderedDict()
    cols = 'id organizacia zariadenie typ druh_1 druh_2 inventarne_cislo rok_nadobudnutia kraj okres obec'.split(' ')
    cols.extend('krajsky_urad ulica c_listu_vlastnictva spoluvlastnicky_podiel vymera parcelne_cislo kolaudacia'.split(' '))
    cols.extend('spravca_objektu uzivatel_objektu obstaravacia_cena_v_EUR zostatkova_cena_v_EUR poznamka'.split(' '))
    
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
    if item['zariadenie'] == '-':
        item['zariadenie'] = None

    # typ
    item['typ'] = row.get('Typ', None)

    # druh
    item['druh_1'] = row.get('Druh', None)
    item['druh_2'] = row.get('Druh2', None)
    
    # inventarne cislo
    item['inventarne_cislo'] = row.get('Inventárne číslo', None)

    # rok nadobudnutia a kraj
    rok_kraj = row.get('Rok nadobudnutia a kraj', None)
    if rok_kraj is not None:
        results = re.findall('^(\d{4}) (.*)$', rok_kraj)
        if results:
            item['rok_nadobudnutia'] = int(results[0][0])
            item['kraj'] = results[0][1]
        else:
            if re.match('^\d{4}$', rok_kraj):
                item['rok_nadobudnutia'] = int(rok_kraj)
            else:
                item['kraj'] = rok_kraj
    
    # okres, obec, krajsky_urad
    item['okres'] = row.get('Názov okresu', None)
    item['obec'] = row.get('Názov obce', None)
    item['krajsky_urad'] = row.get('Názov KÚ', None)

    # ulica
    item['ulica'] = row.get('Ulica', None)
    
    # cisla a podiely
    item['c_listu_vlastnictva'] = row.get('Číslo VL', None)
    item['spoluvlastnicky_podiel'] = row.get('Spoluvl. podiel', None)

    # vymera a parcelne cislo
    vymera = row.get('Výmera v m^2', None)
    if vymera is not None:
        results = re.findall('^([\d ]+,\d+) (.*)$', vymera)
        if results:
            item['vymera'] = results[0][0]
            item['parcelne_cislo'] = results[0][1]
        else:
            if re.match('^[\d ]+,\d+$', vymera):
                item['vymera'] = vymera
        
    pc = row.get('Parcelné číslo', None)
    if pc is not None:
        item['parcelne_cislo'] = row.get('Parcelné číslo', None)

    # datum kolaudacie a spravca objektu
    kol_spr = row.get('Kolaudácia a správca objektu', None)
    spr = row.get('Správca objektu', None)

    if kol_spr is not None:
        results = re.findall('^(\d{4}) (.*)$', kol_spr)
        if results:
            item['kolaudacia'] = int(results[0][0])
            item['spravca_objektu'] = results[0][1]
        else:
            if re.match('^\d{4}$', kol_spr):
                item['kolaudacia'] = int(kol_spr)
            else:
                item['spravca_objektu'] = kol_spr
    if spr is not None:
        item['spravca_objektu'] = spr.strip()

    # uzivatel, obstaravacia a zostatkova cena
    item['uzivatel_objektu'] = row.get('Užívateľ objektu', None)
    item['obstaravacia_cena_v_EUR'] = row.get('Obstarávacia cena v EUR', None)

    # poznamka
    zc = row.get('Zostatková cena v EUR', None)
    if zc is not None:
        results = re.findall('^([\d ]+,\d+) (.*)$', zc)
        if results:
            item['zostatkova_cena_v_EUR'] = results[0][0]
            item['poznamka'] = results[0][1]
        else:
            item['zostatkova_cena_v_EUR'] = zc

    return item

"""
main loop
"""


html = scraperwiki.scrape(site_url + start_page)

# get all pdf links
root = lxml.html.fromstring(html)
pdf_urls = root.cssselect("li.pdf > a")
total_invalid_rows = 0
total_processed_rows = 0
total_pages = 0

for filenum, pdf_url in enumerate(pdf_urls):
    pdf_url_text = site_url + pdf_url.get('href')
    prt(pdf_url_text)

    pdf_text = scraperwiki.scrape(pdf_url_text)
    data = scraperwiki.pdftoxml(pdf_text)

    tree = lxml.etree.fromstring(data)
    #tree = lxml.etree.parse('data.xml')

    missed_rows_page = 0
    processed_rows_page = 0

    for p, page in enumerate(tree.xpath('page')):
        prt("processing page" + page.get('number'))

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

        prt(sorted(rows.keys()))
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
                    prt('Could not match ID:')
                    prt(itemvalues)
                    missed_rows += 1
            else:
                prt('Could not match ID:')
                prt(itemvalues)
                missed_rows += 1
        
        scraperwiki.sqlite.save(unique_keys=['id'],data=pagedata)
        prt("Missed rows: %s" % missed_rows)

        missed_rows_page += missed_rows
        processed_rows_page += len(rows.keys())

    print "File: %s Processed %s pages and %s rows. Skipped %s invalid rows." % (
        filenum+1, p+1, processed_rows_page, missed_rows_page) 
    
    total_invalid_rows += missed_rows_page
    total_processed_rows += processed_rows_page
    total_pages += p + 1

print "\nTOTAL: Files: %s Pages: %s Rows: %s Skipped rows: %s" % (
    filenum+1, total_pages, total_processed_rows, total_invalid_rows) 
