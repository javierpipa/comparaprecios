from django.core.management.base import BaseCommand

from precios.models import (
    Site, 
    SiteMap, 
    SiteURLResults,

)
from viusitemapparser.vsp import get_sitemap_contents


class Command(BaseCommand):
    help = "Start the simulation"

    def __init__(self):
        super().__init__()
        self.links = []
    
    def add_arguments(self, parser):
        parser.add_argument('SiteId', type=int, help='Id of VM to get info')


    def handle(self, *args, **options):
        SiteId = options["SiteId"]
        sites = Site.objects.filter(id=SiteId)
        for thissite in sites:
            this_site_nuevos = 0
            siteMaps = SiteMap.objects.filter(site=thissite, get_url=True)
            for map in siteMaps:
                try:
                    sitemap, sitemap_entries = get_sitemap_contents(map.loc)
                except:
                    print("error")
                    return
                for entry in sitemap_entries:
                    if not SiteURLResults.objects.filter(site=thissite,url=entry.get('loc')).exists():
                        # print(entry.get('loc'))
                        if len(entry.get('loc')) < 500:
                            try:
                                obj_siteMap, created = SiteURLResults.objects.update_or_create(
                                    site=thissite,
                                    url=entry.get('loc')
                                )
                            except ValueError:
                                print("Len Loc = ", len(entry.get('loc')))
                                print(entry.get('loc'))
                        this_site_nuevos += 1
                        
            print(f'Sitio: {thissite.siteName} nuevos={this_site_nuevos}')