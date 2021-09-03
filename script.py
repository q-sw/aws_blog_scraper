from bs4 import BeautifulSoup
from botocore.client import Config
from botocore import exceptions
from pprint import pprint
import requests
import datetime
import json
import os
import boto3

CONFIG_FILE_PATH = os.path.dirname(__file__)
with open(os.path.join(CONFIG_FILE_PATH, 'config.json'), 'r') as config_file:
	config = json.load(config_file)

URL_ENDPOINT = os.environ.get('S3_URL')
ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

def parse_page(url, limit_day):
	r = requests.get(url)
	if (r.status_code != 200) and (r.status_code != 302)  and (r.status_code != 301):
		print(f"ERREUR: url: {url} Status code {r.status_code}")
		return
	else:
		article = get_article(r.content, limit_day)
		if len(article) != 0:
			return article

def get_article(blog_content, limit_day):
	article = []
	soup = BeautifulSoup(blog_content, 'html.parser')

	for blog_article in soup.find_all("div", class_="lb-col lb-mid-18 lb-tiny-24"):
		article_link = blog_article.find('h2', class_="blog-post-title").find('a').get('href')
		article_date = blog_article.find('footer', class_="blog-post-meta").find('time').get('datetime')
		article_date = datetime.datetime.strptime(article_date[:-6], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")
		
		today = datetime.datetime.now().strftime("%d/%m/%Y")
		limit_date = (datetime.datetime.strptime(today, "%d/%m/%Y") - datetime.timedelta(days=limit_day))
		

		if datetime.datetime.strptime(article_date, "%d/%m/%Y") >= limit_date: 
			article.append({article_date: article_link})

	return(article)

def return_article(category, base_url, blog_language, limit_day):
	url = base_url+"/"+category
	key_name = blog_language+"_"+category
	return {key_name: parse_page(url, limit_day)}

def upload_result(url_endpoint, access_key, secret_key, bucket_name, file_path, file_name):
	s3 = boto3.resource('s3',
                    endpoint_url=url_endpoint,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(signature_version='s3v4'),
                    region_name='us-east-1')
	try:
		s3.Bucket(bucket_name).upload_file(file_path, file_name)
		return("")
	except exceptions.EndpointConnectionError:
		print('Erreur: Connexion impossible --> vérifier que le bucket est accessible')

def main():
	all_article = []
	for blog in config.get('blogs'):
		for category in blog['categories']:
			if category['fetch']:
				all_article.append(return_article(
					category["category"], 
					blog['url'], 
					blog['language'], 
					config.get('limit_scrap_day') ))
	
	if config.get('backup_result'):
		file_name = datetime.datetime.now().strftime("%Y%m%d")+"_"+config.get('backup_destination').get('file_name')
		file_path = os.path.join(config.get('backup_destination').get('path'), file_name)
		
		with open(file_path, 'w') as result:
			json.dump(all_article, result, indent=4)

		if config.get('backup_destination').get('type') == "S3":
			BUCKET_NAME = config.get('backup_destination').get('backet_name')
			upload_result(URL_ENDPOINT, ACCESS_KEY, SECRET_KEY, BUCKET_NAME, file_path, file_name)
	else:
		pprint(all_article)
if __name__ == "__main__" :
	main()