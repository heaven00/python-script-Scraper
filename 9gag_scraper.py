from __future__ import with_statement
import os.path
import lxml.html
import simplejson as json
import urllib
import PIL
from PIL import Image
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media,posts
from wordpress_xmlrpc.methods.posts import NewPost


DOWNLOAD_DIR = "/directory_to_place_scrapedimages"
DATA_DIR = "/directory_to_place_cropedimages"


def getimg():
	names = []
	url = urllib.urlopen("http://9gag.com/hot").read()
	img = lxml.html.fromstring(url)
	for source in img.xpath('//div[contains(@class,"img-wrap")]//img/@src'):
		name = source.split('/')[-1]

		download_location = os.path.join(DOWNLOAD_DIR, name)
		urllib.urlretrieve(source, download_location)
		imag = Image.open(download_location)

		x = imag.getbbox()
		box = (x[0],x[1],x[2],(x[3]-30))
		new = imag.crop(box)

		save_location = os.path.join(DATA_DIR, name)
		new.save(save_location)

		names.append(name)
	return names

def gettitle():
	titles =[]
	x = {}
	url = urllib.urlopen("http://9gag.com/hot").read()
	title = lxml.html.fromstring(url)
	for source in title.xpath('//div[contains(@class,"img-wrap")]//img/@alt'):
		titles.append(source)
			
	return titles

def upload(name,title):
	client = Client('http://domain.com/xmlrpc.php','username','password')
	imgfile = os.path.join(DATA_DIR, name)
	#imgfile = 'op/%s'%name
	data = {'name':name,'type':'image/jpg',}
	with open(imgfile,'rb+') as imag:
		data['bits'] = xmlrpc_client.Binary(imag.read())
	response = client.call(media.UploadFile(data))
	attachment_id = response['id']
	_title = lxml.html.fromstring(title).text	
	post = WordPressPost()
	post.title = _title
	post.post_status = 'publish'
	post.thumbnail = attachment_id
	post.comment_status = 'open'
	post.id = client.call(posts.NewPost(post))


if __name__ == '__main__':	
	n = 0
	names = getimg()
	for  i in names:
		titles = gettitle()
		n = n+1

	for i in range(0,n):
		name = names[i]
		title = 	titles[i]
		print name,title
		upload(name,title)
		
