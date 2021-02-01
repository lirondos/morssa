import newspaper
from newspaper import Article
import feedparser
import time
import csv
from datetime import date 
from datetime import datetime, timezone
import json
import dateutil.parser as dateparser
import re
import os
import furl
import csv
import pandas as pd
import yaml
from pathlib import Path
import argparse
import time


parser = argparse.ArgumentParser()
parser.add_argument('param', type=str, help='Path to file with params')
parser.add_argument('root', type=str, help='Path to current directory')



def get_text_date(url):
	try:
		article = Article(url)
		article.download()
		article.html = re.sub(r"\n+", " ", article.html)
		article.html = re.sub(r"<blockquote class=\"twitter-tweet\".+?</blockquote>", "", article.html)
		article.html = re.sub(r"<blockquote class=\"instagram-media\".+?</blockquote>", "", article.html)
		article.html = re.sub(r"<blockquote class=\"tiktok-embed\".+?</blockquote>", "", article.html)
		article.html = re.sub(r"<blockquote cite=\".+?</blockquote>", "", article.html)
		#article.html = re.sub(r"<h2 class=\"mce\">&middot.+?</p>", "", article.html) # subtitulares de vertele
		article.html = re.sub(r"<figcaption.+?</figcaption>", "", article.html)
		article.parse()
		return  article.text, article.publish_date
	except newspaper.article.ArticleException:
		return None, None


if __name__ == "__main__":
	args = parser.parse_args()
	root = Path(args.root)
	param_path = root/ args.param
	today=datetime.now(timezone.utc)
	#param_path = root / "param.yaml"

	with open(param_path, 'r') as stream:
		try:
			param = yaml.safe_load(stream)
		except yaml.YAMLError as exc:
			print(exc)


	out_path = root / param["out"]
	already_seen_path = root/ param["already_seen"]
	filename = today.strftime('%d%m%Y') + ".jsonl"
	output_file = out_path / filename


	already_seen = pd.read_csv(already_seen_path, error_bad_lines=False)

	out = param["out"]

	if not os.path.exists(out):
		os.makedirs(out)


	just_seen = set() # este set sirve para controlar que noticias ya han sido añadidas

	with open(param["urls_file"]) as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			time.sleep(5)
			rss_url = row[0]
			source = row[1]
			category = row[2]
			try:
				feed = feedparser.parse(rss_url)
			except Exception as e:
				print(e)
				print(rss_url)
				continue
			print(rss_url)
			for j in feed["entries"]:
				if not "links" in j:
					continue
				url = furl.furl(j["links"][0]["href"]).remove(args=True, fragment=True).url
				if already_seen['url'].str.contains(url).any() or url in just_seen:
					continue
				text, publish_date = get_text_date(url)
				date = j['published'] if 'published' in j else j['updated']
				if text:
					print(url)
					item = {
							   "text": text,
								"title": j["title"],
						   		"url": furl.furl(url).remove(args=True, fragment=True).url,
								"date": dateparser.parse(date).strftime("%A, %d %B %Y"),
								"source": source,
								"category": category}
					with open(output_file , 'a', encoding = "utf-8") as json_file, open(param["already_seen"], mode='a', newline='', encoding = "utf-8") as csv_file:
						file_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
						json.dump(item, json_file)
						json_file.write('\n')
						file_writer.writerow([item["url"], item["title"], item["date"], item["source"], item["category"]])
