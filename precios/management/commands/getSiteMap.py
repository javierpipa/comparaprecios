from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from precios.models import (
    Site, 
    SiteMap, 
    SiteURLResults,

)
from viusitemapparser.vsp import get_sitemap_contents
import requests
import gzip


class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
        self.links = []
    
    def add_arguments(self, parser):
        parser.add_argument('SiteId', type=int, help='Id of VM to get info')
        
    def GetSiteMap(self, site, siteMapUrl):

        try:
            print("inicio", siteMapUrl)
            if '.gz' in siteMapUrl:
                print("paso 1")
                response = requests.get(siteMapUrl, stream=True)
                print("paso 3")
                with open("./sitemapaso.txt.gz", "wb") as binary_file:
                    binary_file.write(response.content)
                    binary_file.close()
                # f = open('./sitemappaso.txt', 'wb')
                with gzip.open('./sitemapaso.txt.gz', 'rb') as f:
                    file_content = f.read()

                print("paso 4")
                with open("./sitemapaso.xml", "wb") as text_file:
                    text_file.write(file_content)
                    text_file.close()
                # f.write(texto)
                print("paso 5")
                # f.close()
                print("paso 6")
                sitemap, sitemap_entries = get_sitemap_contents('./sitemappaso.xml')
            else:
                sitemap, sitemap_entries = get_sitemap_contents(siteMapUrl)
            # print(sitemap.file_error)
        except Exception as e:
            print("error")
            print(str(e))
            return
            
        for entry in sitemap_entries:

            if sitemap.get("sitemap_type") == 'xml_sitemap_index':
                mifecha = entry.get('lastmod')
                loca = entry.get('loc')
                if mifecha:
                    mifecha = parse_date(mifecha)
                else:
                    mifecha = parse_date('2022-10-24')
                try:
                    obj_siteMap, created = SiteMap.objects.update_or_create(
                        site=site,  
                        loc=loca,
                        defaults={'sitemap_type': sitemap.get("sitemap_type"),'lastmod':mifecha}
                        )
                except Exception as e:
                    
                    print(f'GetSiteMap: error {site.siteName} loc={loca}')
                    print(str(e))
                self.GetSiteMap(site, entry.get('loc'))

        return

    def handle(self, *args, **options):
        SiteId = options["SiteId"]
        
        sites = Site.objects.filter(siteSearch='sitemap', enable=True, pk=SiteId).all()
    
        for site in sites:
            if site.sitemap_url != '':
                siteMapUrl = site.sitemap_url
                self.GetSiteMap(site, siteMapUrl)