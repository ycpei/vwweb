#-------------------------------------------------------------------------------
# Copyright (c) 2017 Yuchen Pei
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------

from os import listdir, path
import datetime
import pydoc
import time
from bib2html import *

htmldir = '../toywiki/html/'
wikidir = '../toywiki/wiki/'
configdir = '../toywiki/config/'
bibfilename = '../toywiki/config/tw.bib'


def assemble(wikiname):
    """
    assemble the html given a wikiname
    """
    content = vimwikihtml2content(wikiname)
    template = open(configdir + 'default.tpl', 'r')
    data = template.read()
    data = data.replace('%title%', gettitle(wikiname))
    data = data.replace('%title%', gettitle(wikiname))
    data = data.replace('%index%', navbar(wikiname))
    data = data.replace('%content%',content)
    data = data.replace('%references%', generatereflist(wikiname))
    data = data.replace('%date%', getdate(wikiname))
    data = removebrokenlinks(data)
    htmlname = wikiname + '.html'
    htmlfile = open(htmldir + htmlname, 'w')
    htmlfile.write(data)

def generatereflist(wikiname):
    keys = generatekeylist(wikiname)
    if keys != []:
        result = '<h2>References</h2><ul>'
        for key in keys:
            result += htmlfrombibkey(bibfilename, key)
        result += '</ul>'
        return result
    return ''

def generatekeylist(wikiname):
    data = open(wikidir + wikiname + '.wiki', 'r').read()
    bibkeylist = list(set(re.findall('\[\{(.*?)\}\]', data)))
    bibkeylist.sort()
    return bibkeylist

def generateallkeylist():
    bibkeylist = []
    namelist = getnamelist()
    for name in namelist:
        bibkeylist += generatekeylist(name)
    bibkeylist = list(set(bibkeylist))
    bibkeylist.sort()
    return bibkeylist

def getnamelist():
    """
    return the list of wikinames
    """
    namelistfile = open(configdir + 'wikilist', 'r')
    namelist = []
    while True:
        name = namelistfile.readline().replace('\n', '')
        if name == '':
            break
        else:
            namelist += [name]
    return namelist



def assembleall():
    """
    assemble all html pages in the namelist
    """
    namelist = getnamelist()
    for name in namelist:
        assemble(name)
        addplaintexttag(name)



def vimwikihtml2content(wikiname):
    """
    truncate the html converted from wiki using vimwiki to the portion fit in %content% in the template
    """
    htmlname = htmldir + wikiname + '.html'
    html = open(htmlname, 'r')
    data = html.read()
    pos1 = data.find('<body>')
    pos2 = data.find('</body>')
    data = data[pos1 + 6 : pos2]
    return data



def navbar(wikiname):
    """
    assemble the left navbar of wikiname.html
    """
    listfile = open(configdir + 'wikilist', 'r')
    data = ''
    data += '<ul>'
    while True:
        n = listfile.readline().replace('\n', '')
        if n == '':
            break
        t = gettitle(n)
        if n != wikiname:
            data += '<li><a href="' + n + '.html">' + t + '</a></li>'
        else:
            data += '<li>' + t + '</li>'
    data += '</ul>'
    return data


def getdate(wikiname):
    """
    parse the date of wikiname.wiki
    if %date field exists then use it, otherwise print a warning and use file modification date
    """
    wikifile = open(wikidir + wikiname + '.wiki', 'r')
    data = wikifile.read()
    pos = data.find('%date')
    if pos == -1:
        print('Warning: ' + wikiname + ' has no date placeholder! Using file modification date...')
        t = path.getmtime(wikidir + wikiname + '.wiki')
        return time.strftime("%Y-%m-%d", time.gmtime(t))
    else:
        pos += 6
        pos1 = data.find('\n', pos)
        return data[pos : pos1]



def gettitle(wikiname):
    """
    parse the title of wikiname.wiki.
    If %title field exists then use it, otherwise use wikiname
    TODO: print warning when no %title exists
    """
    wikifile = open(wikidir + wikiname + '.wiki', 'r')
    data = wikifile.read()
    pos = data.find('%title')
    if pos == -1:
        return wikiname
    pos += 7
    pos1 = data.find('\n', pos)
    rawtitle = data[pos: pos1]
    nd = rawtitle.count('$')
    title = ''
    for i in range(int(nd /  2)):
        fd = rawtitle.find('$')
        sd = rawtitle.find('$', fd + 1)
        title += rawtitle[ : fd] + '\(' + rawtitle[fd + 1 : sd] + '\)'
        rawtitle = rawtitle[sd + 1:]
    title += rawtitle
    return title



def genlist():
    """
    generate a list of the wikinames, namely find all .wiki files and put their file names (without .wiki extension) in 
    a file
    """
    flist = [f for f in listdir(wikidir) if f[-5:] == '.wiki']
    namelist = [f[:-5] for f in flist]
    namelist.sort()
    outfile = open(configdir + 'wikilist', 'w')
    for n in namelist:
        outfile.write(n + '\n')



def removebrokenlinks(html):
    """
    check if a hyper link has a correponding wiki in wikidir
    if not the strip the link.

    this only works assuming the links ends with html (with or without anchor)
    """
    ap1 = html.find('<a href')
    result = html[: ap1]
    while ap1 != -1:
        ap2 = html.find('>', ap1)
        ap3 = html.find('</a>', ap2)
        ap4 = ap3 + 4
        linkp1 = html.find('"', ap1 + 1)
        linkp2 = html.find('"', linkp1 + 1)
        linkp3 = html.find('#', linkp1 + 1, linkp2) #process links with anchors
        if linkp3 == -1:
            linkpath = html[linkp1 + 1 : linkp2 - 5]
        else:
            linkpath = html[linkp1 + 1 : linkp3 - 5]
        linkpath = wikidir + linkpath + '.wiki'
        if (not path.isfile(linkpath)) and (html[linkp1 + 1: linkp1 + 5] != 'http'):
            delta = html[ap2 + 1 : ap3]
        else:
            delta = html[ap1 : ap4]
        ap1 = html.find('<a href', ap4)
        result += delta + html[ap4 : ap1]
    result += html[-1]
    return result

def addplaintexttag(wikiname):
    """
    add plaintext tag so that github won't recognise the wiki files as markdown
    """
    data = open(wikidir + wikiname + '.wiki', 'r').read()
    data = '%%<!-- -*- mode: text; -*- -->\n' + data
    open(wikidir + wikiname + '.wiki', 'w').write(data)

if __name__ == '__main__':
    genlist()
    assembleall()
