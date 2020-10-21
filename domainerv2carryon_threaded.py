import urllib2
import re
import sys
import os
import random
import time
import Queue
import threading
from math import log10, floor
monitor_delay=0.6       #The delay on update if screen
pagescan=1000000000000    #pages to scan
pagestosave=50 #every x pages to save
thr=8            # number of downloader threads
queue_multiplier=1

sitesin='https://www.nhs.uk/'         #website to scan

savetime=1
endtime=0

def round_sig(x, sig=2):
    if x==0:
        x=1
    return round(x, sig-int(floor(log10(x)))-1)
def checkurl():
    
    while 1>0:
        if interrupt==1:
            break        
        try:
            pagename=png.get()
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'NewSearch')]
            f=opener.open(pagename)
            url=f.read()        
            f.close()
            page.put(url)
        except:
##            print pagename,'had some silly error'
            url='/'
interrupt=0

def monitor():
    print ''
    print ''
    oldcnt=0
    movave=[0]*25
    while True:
        if interrupt==1:
            break
        del movave[0]
        perintcnt=pagesscanned-oldcnt
        ppsi=perintcnt/monitor_delay
        movave.append(ppsi)
        pps=sum(movave)/25
        pps=round_sig(pps,3)
##        print moveave
        print '\r                                                           ',
        print '\r',pagesscanned, 'st:', round_sig(savetime),tts,'/',pagestosave, 'pt', round_sig(worker_time_s-worker_time_e),'pps',pps, 'pq:',page.qsize(),'lq:',png.qsize(), len(interlink), len(extlink),
        oldcnt=pagesscanned
        time.sleep(monitor_delay)


        
def linkmanager():
##    global scanned
    global interrupt
    ts1=0
    ts2=0
    while 1>0:
        if interrupt==1:
            break
        try:
            nextlink=interlink.pop()
            png.put(sitesin+nextlink)      
            scanned.add(nextlink)
            ts1=0
            ts2=0
        except:
##            print 'waiting for data', ts1
            time.sleep(1)
            ts1=ts1+1
            if ts1==10:
                if png.qsize()==0:
                    interrupt=1
                    page.put('/')
                interrupt=0
                ts2=ts2+1
                if ts2==10:
                    t=threading.Thread(target=checkurl, args=())
                    t.daemon=True
                    t.start()
                    ts2=0
                    
                
            
def checkinurl(sitein):
    try:
        print sitein
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/17.0')]

        f=opener.open(sitein)
        url=f.read()
        page.put(url)
        f.close()
    except:
        raise

def removetrash(links):
    for x in xrange(len(links)):
        for tr in xrange(len(exl)):
            match2=re.search(exl[tr],links[x])
            if match2:
                links[x]='#'
    links[:] = [x for x in links if x != '#']
    return links

def pageprep():
    pages=page.get()
    links=re.findall(r'(?<=href=").*?(?=")',pages)
    if links==None:
        links='#'
    links=removetrash(links)
    return links

def f5(seq, idfun=None):
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def internal(links):
    for ln in xrange(len(links)):
        match3= re.search(r'http://',links[ln])
        if match3:
            dmnin=links[ln]+'/'
            dmnin=re.search(r'(http://).*?/',dmnin)
            if dmnin:
                dmnin=dmnin.group()
                extlink.add(dmnin)
        else:
            links[ln]=re.sub(r'^/(?!=.*)','',links[ln])
            links[ln]=re.sub(r'/$','',links[ln])
            if links[ln] not in scanned:
                interlink.add(links[ln])

f=open('excludes.txt',"r")
exl=f.read()
f.close()
exl=exl.replace('\n', ' ').replace('\r',' ').replace('\t',' ').replace('     ',' ').replace('    ',' ').replace('   ',' ').replace('  ',' ')
exl=exl.split(' ')
exl=f5(exl)
print 'exludes:'
print exl
try:
    f=open('carryon/scanned.txt',"r")
    scanned=f.read()
    f.close()
    scanned=scanned.split('\n')
    scanned=set(scanned)
    f=open('carryon/external.txt',"r")
    extlink=f.read()
    f.close()
    extlink=extlink.split('\n')
    extlinktemp=set()
    print 'processing old data'
    for c in xrange(len(extlink)):
        dmnin=extlink[c]+'/'
        dmnin=re.search(r'(http://).*?/',dmnin)
        if dmnin:
            dmnin=dmnin.group()
            extlinktemp.add(dmnin)
    print 'done reading!'
    extlink=extlinktemp
    print 'done processing external links!'
    extlinktemp=[]
    f=open('carryon/internal.txt',"r")
    interlink=f.read()
    f.close()
    interlink=interlink.split('\n')
    print 'processing internal links'
    interlink=set(interlink)
    inter=set()
    interlen=len(interlink)
    print 'need to process ', interlen, ' links'
    for i in xrange(len(interlink)):
        value=interlink.pop()
        for tr in xrange(len(exl)):
            match2=re.search(exl[tr],value)
        if not match2:
            inter.add(value)
    interlink=inter
    inter=[]
    print '\r done processing links, NHS ington post!'
    time.sleep(1)
    newrun=0
    pagesscanned=len(scanned)
except:

    newrun=1
    interlink=set()
    extlink=set()
    scanned=set()


if not os.path.isdir('out'):
    os.makedirs('out')
os.chdir('out')
f=open("externalall.txt","w+")
f.close()
pagemax=thr*queue_multiplier
pageinmax=thr*queue_multiplier*10
page=Queue.Queue(pagemax)
png=Queue.Queue(pageinmax)
linkq=Queue.Queue(10000)
starttime=time.clock()
if newrun==1:
    checkinurl(sitesin)
    scanned.add('')
    links=pageprep()
    for sl in xrange(len(links)):
        links[sl]=re.sub(r'^.*'+sitesin[11:],'',links[sl])
        links[sl]=re.sub(r'^/(?!=.*)','',links[sl])
        links[sl]=re.sub(r'/$','',links[sl])
    links = f5(links)
    internal(links)
    pagesscanned=1
    
for tst in range(thr):
    t=threading.Thread(target=checkurl, args=())
    t.daemon=True
    t.start()

t=threading.Thread(target=linkmanager, args=())
t.daemon=True
t.start()
worker_time_e=0
worker_time_s=time.clock()
tts=0

t=threading.Thread(target=monitor, args=())
t.daemon=True
t.start()

while 1>0:
    if pagesscanned>=pagescan:
        break
    pagesscanned=pagesscanned+1
    links=pageprep()
    for sl in xrange(len(links)):
        links[sl]=re.sub(r'^.*'+sitesin[11:],'',links[sl])
        links[sl]=re.sub(r'^/(?!=.*)','',links[sl])
        links[sl]=re.sub(r'/$','',links[sl])
    links = f5(links)
    internal(links)
    if interrupt==1:
        break
    tts=tts+1
##    print '\r',pagesscanned, ' st: ', round_sig(savetime), ' ',tts,'/',pagestosave, ' pt', round_sig(worker_time_s-worker_time_e), ' pq: ',page.qsize(),' lq: ',png.qsize(), len(interlink),
    if pagesscanned%pagestosave==0:
        tts=0
        worker_time_e=worker_time_s
        worker_time_s=time.clock()
        
##        endtime=time.clock()
##        print endtime-starttime, 'time for the last',pagestosave,' pages to process' ,'\n'
##        starttime=time.clock()
##        print len(extlink), 'external links,',  pagesscanned, 'pages done','\n'
##        savetime=0
        savetime=time.clock()
        scannedin="\n".join(scanned)
        extlinkin="\n".join(extlink)
        interlinkin="\n".join(interlink)
        f=open("scanned.txt","w+")
        f.write(scannedin)
        f.close()
        f=open("external.txt","w+")
        f.write(extlinkin)
        f.close()
        f=open("internal.txt","w+")
        f.write(interlinkin)
        f.close()
        savetime=time.clock()-savetime
interrupt=1        
print '\n', len(extlink), 'external links', pagesscanned, 'pages done'
print pagesscanned, 'scanned', len(interlink), 'to scan'
extlink=f5(extlink)
extlink.append('')
scanned="\n".join(scanned)
extlink="\n".join(extlink)
interlink="\n".join(interlink)

f=open("scanned.txt","w+")
f.write(scanned)
f.close()
f=open("externalall.txt","a")
f.write(extlink)
f.close()
f=open("internal.txt","w+")
f.write(interlink)
f.close()
print "finished scanning"
os.system('pause')
