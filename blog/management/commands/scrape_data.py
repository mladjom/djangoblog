# # blog/management/commands/scrape_data.py
# from django.core.management.base import BaseCommand
# from blog.utils.scraper_utils import fetch_html, parse_content, save_articles

# class Command(BaseCommand):
#     help = 'Scrapes articles from a target website'

#     def handle(self, *args, **kwargs):
#         url = "https://example.com/articles"
#         html = fetch_html(url)
#         data = parse_content(html)
#         save_articles(data)
#         self.stdout.write(self.style.SUCCESS('Scraping completed!'))
