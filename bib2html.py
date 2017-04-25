# -*- coding: utf-8 -*-

'''Convert utility from bibtex to html'''

# --------------------------------------------------------------------------------
# Copyright (C) 2011 by Bjørn Ådlandsvik and Björn Stenger 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# --------------------------------------------------------------------------------
# Python script to convert bibtex to html (4.01)
#
# Usage:
# bib2html [bibfile] [htmlfile]
# 
# Currently not a full bibtex parser.
# Restrictions:
#   entries must end with "}" in first column of a new line
#   no blank lines allowed within an entry
#   must have space before and after the "=" in the field definitions
#   limited special symbols (accents etc.)
#
# Fields such as author, year, title, ... are marked with <span class=...>
# in the html file. Appearance can be controlled with a CSS style sheet.
# Selected authors (for instance yourself, your research group)
# can be set in the selected_author list (surname only).
# They will be marked by <span class="selected>.
#
# A url field is transferred as [ link ] to the html file,
# if url is missing and doi is presented a url is created,
# A pdf field can point to a local pdf file
#
# Italic text (such as latin species names) may be marked with
# \emph{ ... } in the bibtex file. This is handled correctly
# by both bib2html and LaTeX.
#
# --------------------------------------------------------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
#
# Björn Stenger [bjorn@cantab.net]
# Toshiba Research Europe
# --------------------------------------------------------------------------------
#
# This script has been modified for vwweb by Yuchen Pei
# https://github.com/ycpei/vwweb

import os
import sys
import re
import datetime
import codecs
class KeyNotInBib(Exception):
    pass

# --------------------------------------------------------------------------------
# user settings
# --------------------------------------------------------------------------------


# output html encoding
#encoding = 'UTF-8'
encoding = 'ISO-8859-1'

# html page title
title = u'Publication List'

# list of authors for which the font can be changed
selected_authors = [u'Yournamehere,']

# location of pdf-files 
#pdfpath = './pdf'
pdfpath = 'http://mi.eng.cam.ac.uk/~bdrs2/papers/'

# css style file to use
css_file = 'style.css'

# html prolog
# modify according to your needs
prolog = """<!DOCTYPE HTML
    PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<head>
  <meta http-equiv=Content-Type content="text/html; charset=%s">
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="%s">
  <style type="text/css">     
     span.selected {color: #000000}
     span.author {color: #000000}
     span.title {font-weight: bold;}
     li {margin-top: 0px; margin-bottom: 16px}
  </style>
</head>
<body>

<div class="header">
<strong>&nbsp;&nbsp;&nbsp;Bj&ouml;rn Stenger</strong><br> 
&nbsp;&nbsp;&nbsp;Computer Vision Group, Toshiba Research Europe
</div>

<div class="container">
<ul id="miniflex">
	<li><a href="index.html">home</a></li>
	<li><a href="research.html">research</a></li>
	<li><a href="pubs.html" class="active">publications</a></li>
</ul>
</div>

<div id="content">
<h2>
[<a href="bjornstenger.bib"  target="_top">BibTeX file</a>]&nbsp;
</h2>
<br>
""" % (encoding, title, css_file)

# now = yyyy-mm-dd
now = str(datetime.date.today())

# html epilog
epilog = """
<br>
<hr>
Created %s with <a href="bib2html.py">bib2html.py</a>
</p>
</div>
</body>
</html>
""" % (now)







# --------------------------------------------------------------------------------
# class and function definitions
# --------------------------------------------------------------------------------

# regular expression for \emph{...{...}*...}
emph = re.compile(u'''
            \\\\emph{                       # \emph{
            (?P<emph_text>([^{}]*{[^{}]*})*.*?)  # (...{...})*...
            }''', re.VERBOSE)               # }



# --------------------------------------------------------------------------------
# class: bibtex entry 
# --------------------------------------------------------------------------------
class Entry(object):
    """Class for bibtex entry"""

    def clean(self):
        '''Clean up an entry'''
        for k, v in self.__dict__.items():

            # remove leading and trailing whitespace
            v = v.strip()

            # replace special characters - add more if necessary
            v = v.replace('\\AE', u'Æ')
            v = v.replace('\\O',  u'Ø')
            v = v.replace('\\AA', u'Å')
            v = v.replace('\\ae', u'æ')
            v = v.replace('\\o',  u'ø')
            v = v.replace('\\^o',  '&ocirc;')
            v = v.replace('\\aa', u'å')
            v = v.replace('\\"a', '&auml;')
            v = v.replace('\\\'a', '&aacute;')
            v = v.replace('\\\'e', '&eacute;')
            v = v.replace('\\c{c}' , '&ccedil;')

            # fix \emph in title
            if k == 'title':
                v = re.sub(emph, '<I>\g<emph_text></I>', v)

            # remove "{" and "}"
            v = v.replace('{', '')
            v = v.replace('}', '')
            v = v.replace('"', '')
        
            # remove trailing comma and dot
            if len(str(v))>0:
              if v[-1] == ',': v = v[:-1]

            # fix author
            if k == 'author':

                # split into list of authors
                authors = v.split(' and ')

                # strip each author ;)
                authors = [a.strip() for a in authors]

                # make blanks non-breakable
                authors = [a.replace(' ', '&nbsp;') for a in authors]

                # reverse first and surname
                for i, a in enumerate(authors):
                    #print a + "\n"
                    #surname = 
                    namearray = a.split('&nbsp;')
                    if namearray[0][-1] == ',':
                        surname = namearray[0]
                        surname = surname.replace(',', '')
                        firstname = ' '.join(namearray[1:])
                        authors[i] = firstname + " " + surname
                    else:
                        authors[i] = ' '.join(namearray)
                

                # mark selected authors - if there are any
                #for i, a in enumerate(authors):
                #    surname = a.split('&nbsp;')[0]
                #    if surname in selected_authors:
                #        a = ''.join(['<span class="selected">', a, '</span>'])
                #        authors[i] = a



                # concatenate the authors again
                #if len(authors) == 1:
                #    v = authors[0]
                #elif len(authors) == 2:
                #    v = authors[0] + " and " + authors[1]
                #else:  # len(authors) > 2:
                #    v =  ", ".join(authors[:-1]) + " and " + authors[-1]
                v = ", ".join(authors[:])

            # fix pages
            if k == 'pages':
                v = v.replace('--', '&ndash;')
                v = v.replace('-',  '&ndash;')
        
            setattr(self, k, v)
        
    # ------------------ 

    def write(self):
        """Write entry to html file"""

        edict = self.__dict__  # bruke
        
        result = ''

        # --- Start list ---
        result += '\n'
        result += '<li>\n'
        
        # --- key ---
        result += '[' + edict['key'] + '] '

        # --- chapter ---
        chapter = False
        if 'chapter' in edict:
          chapter = True
          result += '<span class="title">'
          result += self.chapter
          result += '</span>'
          result += ', '

         

        # --- title ---
        if not(chapter):
            result += '<span class="title">'
            result += self.title
            result += '</span>'
            result += ', '


        # --- author ---
        result += '<span class="author">'
        result += self.author
        result += '</span>'
        result += ', '
        
        # -- if book chapter --
        if chapter:
          result += 'in: '
          result += '<i>'
          result += self.title
          result += '</i>'
          result += ', '
          result += self.publisher


        # --- journal or similar ---
        journal = False
        if 'journal' in edict:
            journal = True
            result += '<i>'
            result += self.journal
            result += '</i>'
        elif 'booktitle' in edict:
            journal = True
            result += edict['booktitle']
        elif edict['type'] == 'phdthesis':
            journal = True
            result += 'PhD thesis, '
            result += edict['school']
        elif edict['type'] == 'techreport':
            journal = True
            result += 'Tech. Report, '
            result += edict['number']
    
        # --- volume, pages, notes etc ---
        if 'volume' in edict:
            result += ', Vol. '
            result += edict['volume']
        if ('number' in edict and edict['type']!='techreport'):
            result += ', No. '
            result += edict['number']
        if 'pages' in edict:
                result += ', p.'
                result += edict['pages']
        elif 'note' in edict:
            if journal or chapter: result += ', '
            result += edict['note']
        if 'month' in edict:
            result += ', '
            result += self.month

        # --- year ---
        result += '<span class="year">'
        #result += ', ';
        result += ' ';
        result += self.year
        result += '</span>'
        #result += ',\n'

        # final period
        result += '.'

        # --- Links ---
        pdf = False
        url = False
        if 'pdf' in edict:
            pdf = True
        if 'url' in edict or 'doi' in edict:
            url = True

        if pdf or url:
            result += ' \n[&nbsp;'
            if pdf:
                result += '<a href="'
                result += pdfpath + self.pdf
                result += '">pdf</a>&nbsp;'
                if url:
                    result += '\n|&nbsp;'
            if url:
                result += '<a href="'
                if 'url' in edict:
                    result += self.url
                else:
                    result += 'http://dx.doi.org/' + self.doi
                result += '">link</a>&nbsp;'
            result += ']\n'

        # Terminate the list entry
        result += '</li>\n'
        return result



# --------------------------------------------------------------------------------
# generator: bibtex reader
# --------------------------------------------------------------------------------
def bib_reader(filename):
    '''Generator for iteration over entries in a bibtex file'''

    fid = open(filename)

    while True:

        # skip irrelevant lines
        while True:
            line = fid.next()
            if len(line) > 0:
                if line[0] == '@': break           # Found entry

        # Handle entry
        if line[0] == '@':
            e = Entry()

            # entry type mellon @ og {
            words = line.split('{')
            e.type = words[0][1:].lower()
            #print e.type + '\n'

            # Iterate through the fields of the entry
            first_field = True
            while True: 
                line = fid.next()
                #print line + '\n'
                words = line.split()
                
                if words[0] == "}": # end of entry
                    # store last field
                    setattr(e, fieldname, fieldtext)
                    break

                if len(words) > 1 and words[1] == "=": # new field
                    # store previous field
                    if not first_field:
                        setattr(e, fieldname, fieldtext)
                    else:
                        first_field = False
                    #inline = True
                    fieldname = words[0].lower()
                    fieldtext = " ".join(words[2:]) # remains a text

                else:  # continued line
                    fieldtext = " ".join([fieldtext] + words)
                
        yield e
        


def locateinbib(fn, key):
    data = open(fn).read()
    m = re.search('^@.*{' + key + ',\s*$', data, re.MULTILINE)
    if m is not None:
        ps = m.start(0) #position of start of a bib record
        pattern = re.compile('^}$', re.MULTILINE)
        pe = pattern.search(data, ps).start(0) #position of end of a bib record
        return ps, pe
    else:
        raise KeyNotInBib



def bibquery(fn, key):
    ps, pe = locateinbib(fn, key)
    data = open(fn).read()
    lines = data[ps : pe].split('\n')
    e = Entry()
    e.key = key
    e.type = re.search('@(\w+){', lines[0]).group(1).lower()
    for s in lines[1:-1]:
        fieldname = re.search('^\s*(\w+?)\s*=', s).group(1).lower()
        fieldtext = re.search('=\s*(.*)\s*', s).group(1)
        setattr(e, fieldname, fieldtext)
    return e



def htmlfrombibkey(fn, key):
    try:
        e = bibquery(fn, key)
        e.clean()
        return e.write()
    except KeyNotInBib:
        print('can not find ' + key + ' in bib!')
        return '\n<li>[' + key + ']</li>\n'



def bibkeylist2htmlfile(fn, keys):
    f = open(fn, 'w')
    for key in keys:
        f.write(htmlfrombibkey(key))




# --------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------
def main():

  args = sys.argv[1:]

  if not args:
      bibfile="bjornstenger.bib"
    #print 'usage: bib2html [bibfile] [htmlfile]'
    #sys.exit(1)
  else:
      bibfile=args[0]
      del args[0:1]

  if not args:
    htmlfile="publist.html" #default
  else:
    htmlfile=args[0]

  #print "bibfile :"+bibfile+"\n"
  #print "htmlfile :"+htmlfile+"\n"

  # create the html file with opted encoding 
  f1 = codecs.open(htmlfile, 'w', encoding=encoding)

  # write the initial part of the file
  f1.write(prolog)

  # lists according to publication type
  bookchapterlist =[]
  journallist =[]
  conflist =[]
  techreportlist =[]
  thesislist =[]


  # read bibtex file
  f0 = bib_reader(bibfile)

   # Iterate over the entries and bib2html directives
  for e in f0:  
    e.clean()
    if (e.type=="inbook"):
      bookchapterlist.append(e)
    if (e.type=="article"):
      journallist.append(e)
    if (e.type=="inproceedings"):
      conflist.append(e)
    if (e.type=="techreport"):
      techreportlist.append(e)
    if (e.type=="phdthesis"):
      thesislist.append(e)

  # write list according to publication type

  f1.write('<h2>Journals</h2>');
  f1.write('\n<ol reversed>\n\n')
  for e in journallist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Conferences and Workshops</h2>');
  f1.write('\n<ol reversed>\n\n')
  for e in conflist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Book Chapters</h2>');
  f1.write('\n<ol reversed>\n\n')
  for e in bookchapterlist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Technical Reports</h2>');
  f1.write('\n<ol reversed>\n\n')
  for e in techreportlist:
    e.write(f1)
  f1.write('\n</ol>\n\n')

  f1.write('<h2>Thesis</h2>');
  f1.write('\n<ol reversed>\n\n')
  for e in thesislist:
    e.write(f1)
  f1.write('\n</ol>\n\n')
    
  # write epilog
  f1.write(epilog)
  f1.close()
  
  #print 'written: '+htmlfile+'\n'

if __name__ == '__main__':
  main()
