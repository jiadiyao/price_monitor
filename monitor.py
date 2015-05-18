#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
from time import sleep
from urlparse import urlsplit,urlparse
import urlparse as urlp
import time
import os
import subprocess
import Image
import random
import sys
import MySQLdb
from datetime import datetime
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from cache import CacheHandler
from os.path import basename
import string
#from html2text import html2text
from send_mail import send_mail





forceredo = True






parent_folder = 'psdchest'



proxy=False

#con_rsn = MySQLdb.connect (
#            host = "localhost",
#            user = "root",
#            passwd = "Southampton11",
#            db = "uielements",
#            use_unicode = True,
#            charset = "utf8",)
#cursor = con_rsn.cursor()

##record process start time:
timestarted = datetime.now()
print "Process Started: "+str(timestarted)














#############################
#######utilities###########
##########################

def get_status_code(url):
    try:
        connection = urllib2.urlopen(url)
        return connection.getcode()
        connection.close()
    except urllib2.HTTPError, e:
        return e.getcode()




def isRejected(page):
	return False

##take url, return page
## trys -- number of trys before give up
##
def opener(url,trys=10,ran_begin=2,ran_end=10):
	path = os.path.abspath('cache')
	proxy_handler = urllib2.ProxyHandler({'http': 'http://127.0.0.1:8118/'})
	
	if proxy:
		##opener with cache
		urlopener = urllib2.build_opener(CacheHandler(path, max_age = 604800),proxy_handler)
		urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9) Gecko/20100402 Ubuntu/9.10 (karmic) Firefox/3.5.9')]
		
		##opener skip cache:
		urlopener_nocache = urllib2.build_opener(proxy_handler)
		urlopener_nocache.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9) Gecko/20100402 Ubuntu/9.10 (karmic) Firefox/3.5.9')]
	else:
		##opener with cache
		urlopener = urllib2.build_opener(CacheHandler(path, max_age = 604800))
		urlopener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9) Gecko/20100402 Ubuntu/9.10 (karmic) Firefox/3.5.9')]
		
		##opener skip cache:
		urlopener_nocache = urllib2.build_opener()
		urlopener_nocache.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.1.9) Gecko/20100402 Ubuntu/9.10 (karmic) Firefox/3.5.9')]
		
	##page  -- null page means run the retry loop
	page=''
	##toretry  -- set to 1 to run the retry loop
	toretry=0
	##isRejected -- page reject means retry loop (waiting and ip renew should be done while in the retry loop)
	
	firstrun = 1
	while ((not page) or toretry or isRejected(page)) and trys!=0:
	
		try:
			request = urllib2.Request(url)
			failed = 1
			while failed:
				try:
					##only first time open the url use the cached version.
					if firstrun:
						resp = urlopener.open(request,None,30)
						firstrun=0
					else:
						resp = urlopener_nocache.open(request,None,30)
					
					failed = 0
				except urllib2.URLError, e:
					if hasattr(e, 'reason'):
						print 'We failed to reach a server.'
						print 'Reason: ', e.reason
					elif hasattr(e, 'code'):
						print 'rejected'
						print 'Error code: ', e.code
					
					print 'sleep 600'
					sleep(600)
		
		
			realurl = resp.url
			if realurl != url:
				print "[ERROR] been redirected. Sleep 600s to wait ip renewal"
				toretry=1
				sleep(600)
				
				
				
			page = resp.read()
			page = page.decode('utf8', 'ignore')
			if not 'x-cache' in resp.headers:
				t = random.randint(ran_begin, ran_end)
				print 'not from cache, sleeping...',t
				sleep(t)
		
		
		
		
		
#			resp = urlopener.open(url,None,30)
#			page = resp.read()
#			page = page.decode('utf8', 'ignore')
#			pageincache = 'x-cache' in resp.headers
#			#print 'Page is from cache:', pageincache
#			
#			
#			if pageincache and (not page):
#				print "cache corrupted, reopen... ", url
#				##if cache is courrpted
#				resp = urlopener_nocache.open(url,None,30)
#				page = resp.read()
#				page = page.decode('utf8', 'ignore')
#				
#			
#			
#			##if not from cache, sleep
#			if not 'x-cache' in resp.headers:
#				t = random.randint(ran_begin, ran_end)
#				print 'not from cache, sleeping...',t
#				sleep(t)
#			#sleep(5)	
				
		except:
			page=''
			t = 60
			print 'Waiting to retry...',t
			sleep(t)
		trys=trys-1
	if not page:
		print '~~ERROR: Opening url ',url
		
	return page



def url2name(url):

    return basename(urlsplit(url)[2])
    
    
##Take a url, save the file pointed by the url.
## handles redirections    
def download(url, path, localFileName = None):
	try:
	
		localName = url2name(url)
	

		req = urllib2.Request(url)
		r = urllib2.urlopen(req)
		if r.info().has_key('Content-Disposition'):
			# If the response has Content-Disposition, we take file name from it
			localName = r.info()['Content-Disposition'].split('filename=')[1]
			if localName[0] == '"' or localName[0] == "'":
				localName = localName[1:-1]
		elif r.url != url: 
			# if we were redirected, the real file name we take from the final URL
			localName = url2name(r.url)

		if localFileName: 
			# we can force to save the file as specified name
			localName = localFileName
	
	

		f = open(path+'/'+localName, 'wb')
		f.write(r.read())
		f.close()

		return localName
	except:
		return False
	

#######################################################
###########getting various parts:
#################################
def get_title(soup):
	title = ''
	#if 1:
	try:
		titleTag = soup.html.head.title
		title = titleTag.string.split(' - ')[0]
		title = html2text(title)  
		#print title
	except:
		print "[title failed]"

	return title.strip()




##find images on the post, save the images to the post folder. returns the foldername for the post
## 
def find_images(soup):
	##mkdir:
	folder = get_title(soup)
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	foldername = ''.join(c for c in folder if c in valid_chars)
	foldername = foldername.replace(' ','_')
	
	
	folderpath = parent_folder+'/'+foldername
	print 'download images...'



	##create preview folder
	
	prevfolderpath = folderpath+'/previews'
	
	try:
		os.makedirs(prevfolderpath)
	except OSError:
		pass
	
	
	
	
	###############################
	##find the THUMBNAIL image:
	try:
		os.makedirs(folderpath)
	except OSError:
		pass
	imgurl = soup.find('div',{'class':'pic2 fl'}).findAll('img')[-1]['src']
	print imgurl
		
	###save image binary data in a dictionary
	imgname = url2name(imgurl)
#	data = opener(imgurl)
#	rtn[imgname] = data
	
	##download the image using the download function
	saved_name = download(imgurl,folderpath)
	download(imgurl,prevfolderpath)
	
	##############################
	## resize the thumbnail to 200x144
	size = 200,144
	ratio = 1.*200/144
	try:
		im = Image.open(folderpath+'/'+saved_name)
		(width, height) = im.size
		if width<=size[0] and height<=size[1]:
			print 'no resize'
			im.save(folderpath+'/thumbnail.jpg', "JPEG",quality=100)
		else:
		
			if width > height * ratio:
				# crop the image on the left and right side
				newwidth = int(height * ratio)
				#left = width / 2 - newwidth / 2
				left = 0
				right =  newwidth
				# keep the height of the image
				top = 0
				bottom = height
			elif width < height * ratio:
				# crop the image on the top and bottom
				newheight = int(width / ratio)
				top = 0#height / 2 - newheight / 2
				bottom = newheight
				# keep the width of the impage
				left = 0
				right = width
			if width != height * ratio:
				im = im.crop((left, top, right, bottom))

			out = im.resize(size, Image.ANTIALIAS)
			out.save(folderpath+'/thumbnail.jpg', "JPEG",quality=100)
	except IOError:
		print "cannot create thumbnail for '%s'" % saved_name



	################################
	
	
	#print rtn.keys()
	#raw_input('sdf')
	
	
	#########################
	##### MORE PREVIEW IMAGES
#	imgs = content.find('div',{'class':'entry'}).findAll('img')
#	for im in imgs:
#		imgurl = im['src']
#		download(imgurl,prevfolderpath)
		
	
	
	
	return foldername




##get the free download, save to the correct folder.
##return filename when successfully saved file, return False when not
def get_downloadfile(soup,url=''):
	
	downloadurl= soup.find('img',src = 'http://www.shegy.nazwa.pl/psdchest/wp-content/plugins/smartcounter/download_button.png' ).parent['href']
	print downloadurl

	
	##adding baseurl to reletive url:
#	if not downloadurl.startswith('http'):
#		downloadurl = 'http://designmoo.com'+downloadurl
		#print downloadurl

	#print 'download url:',downloadurl
	
	#if not downloadurl.startswith('http'):
	#u = urlparse(downloadurl)
	#print u.query
	#downloadurl = 'http://freepsdfiles.net/get-file/?'+u.query
	
	#print downloadurl
	

	

	folder = get_title(soup)
#	print folder
#	exit()
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	foldername = ''.join(c for c in folder if c in valid_chars)
	foldername = foldername.replace(' ','_')
	folderpath = parent_folder+'/'+foldername
	print 'download files...:',downloadurl
	try:
		os.makedirs(folderpath)
	except OSError:
		pass
	rst = download(downloadurl,folderpath)	
	
	
	
	if rst:
		print 'downloaded file:', rst
		return rst
	else:
		return False 



##get tags for the post:
def get_tags(soup):
	rtn = []
	try:
		tags = soup.find('p',{'class':'meta-nfo'}).findAll('a')

		for tag in tags:
			#print tag.string
			rtn.append(tag.string)
	except:
		pass
		
	##remove last item as it is not tag:
	rtn	= rtn[0:-1]
	return rtn



def get_desc(soup):
	rtn = ''
	try:
		desc = soup.find('div',{'class':'single-post'}).find('h6')
		desc = str(desc).decode('utf8')



		###filter out unwanted tags:
		desc = desc.replace('<h6>','',1)
		desc = re.sub('</h6>.*$','',desc)

		#rtn = html2text(desc)  
		rtn = desc

	except:
		pass
	return rtn
	
def get_creator(soup):
	
	creator = 'Shegy'
	creator_url = 'http://www.psdchest.com'
	
#	try:
#		cont = soup.find('div',{'class':'user_meta'}).find('a')
#		creator = cont.string
#		creator_url = 'http://designmoo.com'+cont['href']
#		#print creator, creator_url
#
#
#	except:
#		pass
	return creator, creator_url
	
##function to process a post
##url, url to a single post
##if download the source file fail, will just return without saving to the database
def post_process(soup,url=''):
	##check for post existance:
	post_exist = cursor.execute('SELECT id FROM post where source_url=%s',(url))
	if post_exist == 0 or forceredo:
	
		downloadname = get_downloadfile(soup,url)
	
		if not downloadname:
			print '[download file failed] skip'
			return		
#			
#		exit()
			
		title = get_title(soup)
		

		tags = get_tags(soup)
		
#		print tags
#		exit()
		
		desc = get_desc(soup)

#		print desc
#		exit()

	
		creator,creator_url = get_creator(soup)
#		print creator
#		print creator_url
#		exit()
		foldername = find_images(soup)
	
		
		
		


	
	
		##insert current post:
		print '[insert post]', title.encode('utf8')
		cursor.execute('insert into post (title,description,html,creator,creator_url,source_url,foldername,downloadname,parentfolder,date_created,date_modified) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())',(title,desc,soup,creator,creator_url,url,foldername,downloadname,parent_folder))
		id = int(cursor.lastrowid)


		##check and insert tags:
		for t in tags:
			###insert keyword to keyword table if not exist:
			query = 'select id from tag where tag=%s'
			kwexist = cursor.execute(query,(t))
			keywords = cursor.fetchone()
			if kwexist==0:
				##insert:
				query = 'INSERT INTO tag (tag) VALUES (%s)'
				cursor.execute(query,(t))
				kwid = cursor.lastrowid
				print '[insert tag] tag insert at id :',kwid
			else:
				kwid = keywords[0]
				print '[nothing] keyword id retrived:',kwid

			##insert tag relations:
			query = "INSERT INTO post_tag (post_id,tag_id) VALUES (%s,%s)"
			cursor.execute(query,(id,kwid))
			print '[insert link tag-post] linked between post and tag:',id,'--',kwid
		
		n=5
		print 'post download and insert successfully, sleep',n
		sleep(n)	
		
	else:
		print '[POST EXIST] SKIP', url




#page = opener('http://freepsdfiles.net/web-elements/free-web-ui-set-navigations-buttons-circles-and-ribbons/')
#soup = BeautifulSoup(page)
#post_process(soup,'http://freepsdfiles.net/web-elements/free-web-ui-set-navigations-buttons-circles-and-ribbons/')
#exit()
##take a start page, process all the post listed on the start page
def post_warpper(url):
	###########process the posts listed on this page:
	page = opener(url)
	postlistsoup = BeautifulSoup(page)
	print '[post list]:',url
	#try:
	if 1:
		items = postlistsoup.findAll('div',{'class':'post'})
		for i in items:
			##process each individual post:
			#print i
			url = i.find('a')['href']
			print '[POST]',url
			page = opener(url)
			soup = BeautifulSoup(page)
			post_process(soup,url)
		#raw_input('page 1 done')
	#except:
	#	print '[POST Fail]',url
		
	
	################
	##baseurl for pagination
	##get url programmingly
	##baseurl = postlistsoup.find('div',{'class':'navigation'}).find('span', {'class':'older'}).find('a')['href'].rsplit('/',2)[0]+'/'
	
	##set base url manually
	baseurl = 'http://www.psdchest.com/page/'
	print baseurl
	#raw_input('___')	


	
	##process each pages
	for p in range(2,4):
		#print p
		pageurl = baseurl+str(p)+'/'
		print '#################\n[post list url]:', pageurl
		st = str(get_status_code(pageurl))
		print 'Status code:', st

		if st == '404':
			print 'break out pagenation loop now!'
			break
		
		
			
		page = opener(pageurl)
		postlistsoup = BeautifulSoup(page)

		try:
			items = postlistsoup.findAll('div',{'class':'post'})
			for i in items:
				##process each individual post:
				#print i
				url = i.find('a')['href']
				print '[POST]',url
				page = opener(url)
				soup = BeautifulSoup(page)
				post_process(soup,url)
			#raw_input('here')
		except:
			print 'Failed:', url

		
	


##get data. 
##given a soup for university box on the university list, 
##return a list of data
##[university name, description, image_url, location, fee, times rank,satisfaction,int% ,id_code_for_course]
	
def get_data(soup):
#	print soup
	name = soup.select(".t1")[0].string
#	print name
	desc = soup.select(".summary")[0].p.string
#	print desc
	imageurl = soup.select(".col01")[0].img['src']
#	print imageurl
	attrs = soup.select(".cols02")[0].select(".col01")
	for attr in attrs:
		if re.search("Satisfaction",attr.img['alt']): 
			
			sat = attr.img.next_sibling.strip()
#			print sat
		elif re.search("Location",attr.img['alt']):       
                        
                        loc = attr.img.next_sibling.strip()
 #                       print loc

		elif re.search("Tuition",attr.img['alt']):     
                        fee = attr.img.next_sibling.strip()
  #                      print fee
		elif re.search("Rank",attr.img['alt']):     
                        rank = attr.img.next_sibling.strip()
   #                     print rank
		else:    
                        international = attr.img.next_sibling.strip()
    #                    print international

	idcode = soup.select(".add")[0].a['href'].split('/')[4].split('?')[0]
#	print idcode


	return (name, desc, imageurl,loc ,fee,rank,sat,international,idcode)












def isemail(log,price,n=1):
	
	stdin,stdout = os.popen2("tail -n "+str(n)+" "+log)
	stdin.close()
	lines = stdout.readlines(); stdout.close()

	lastprice = lines[0].split('\t')[2]
#	print "cur:",price
#	print 'last:',lastprice

	if float(lastprice)!=float(price):
		return 1
	else:
		return 0
















url = "https://www.thomasexchange.co.uk/currency.asp"
page = opener(url)
soup = BeautifulSoup(page)
block = soup.find(id='comparison_rates_tbl').find_all('tr')[2].find_all('td')


eb = block[3].text
es = block[4].text

if not (eb and es): 
	print "ERROR, buy or sell value not get."
	exit()


out = str(datetime.now())+'\t' + str(eb)+'\t'+str(es)+"\n"

toemail = isemail('./pricelog.txt',es)
f1=open('./pricelog.txt', 'a+')
f1.write(out)
f1.close()


mailcontent = "Euro now selling at: "+es+" at Thomas Exchange.\n\n Online reserve: https://www.thomasexchange.co.uk/currency_collect.asp \n\n\n Jiadi "

if float(es) > 1.36 and toemail:
	send_mail(mailcontent.encode("utf8") , es)





exit()







				

	
	

#post_warpper('http://freepsdfiles.net/category/web-elements/')
#post_warpper('http://freepsdfiles.net/category/buttons/')

#page = opener('http://designmoo.com/4101/purse-icon/')
#p = BeautifulSoup(page)
#post_process(p)

#post_warpper('http://www.psdchest.com')



##time finished:
timefinished = datetime.now()
print "Time finished:"+str(timefinished)
print "Time taken: "+ str(timefinished-timestarted)
print "--------------------------------\n\n\n"
exit(0)





