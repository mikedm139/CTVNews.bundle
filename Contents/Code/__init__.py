RE_CLIPID   = Regex('clip.id = ([0-9]+)')
RE_SUMMARY  = Regex('clip.description = "(.+)";')

PREFIX          = '/video/ctvnews'
NAME            = 'CTV News'
CTV_URL         = 'http://www.ctvnews.ca'
VIDEO_URL       = 'http://www.ctvnews.ca/video?clipId=%s&binId=%s'
PLAYLIST_URL    = "%s/%s?ot=example.AjaxPageLayout.ot&pageNum=%d&maxItemsPerPage=12"
EPISODE_URL     = "http://www.ctvnews.ca/video?playlistId=%s&binId=%s" #playlistId, binId

####################################################################################################
def Start():

    ObjectContainer.title1 = 'CTV News'

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():

    oc = ObjectContainer()
    data = HTML.ElementFromURL(CTV_URL + '/video')
    oc.add(DirectoryObject(key=Callback(LocalStations), title="Local News"))
    for section in data.xpath('//dt[contains(@class, "videoPlaylistCategories")]'):
        section_id = section.get('id')
        title = section.xpath('.//a')[0].text
        oc.add(DirectoryObject(key=Callback(SectionMenu, section_title=title, section_id=section_id), title=title))

    return oc

####################################################################################################
@route(PREFIX + '/section', page_num=int)
def SectionMenu(section_title, section_id, url=CTV_URL, page_num=1):
    oc = ObjectContainer(title2=section_title)
    data = HTML.ElementFromURL(PLAYLIST_URL % (url, section_id, page_num))
    for article in data.xpath('//article'):
        try: title = article.xpath('.//p[@class="videoPlaylistDescription"]')[0].text
        except: title = article.xpath('.//h3[@class="videoPackageTitle"]/a')[0].text
        thumb = article.xpath('.//img')[0].get('src').replace('box_180', 'landscape_960').replace('landscape_150', 'landscape_960')
        try:
            clipId = article.xpath('./a')[0].get('id')
            try:
                summary = ''
                for clip in data.xpath('//script'):
                    if "playlistMap['%s'].push(clip)" % clipId in clip.text:
                        description = RE_SUMMARY.search(clip.text).group(1).replace("\\'", "'")
                        summary = summary + description + '\n'
                    else:
                        pass
            except:
                summary = article.xpath('.//p[contains(@class, "videoPlaylistDescription")]')[0].text
            oc.add(VideoClipObject(url=EPISODE_URL % (clipId, section_id), title=title, summary=summary,
                thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
        except:
            try:
                clipId = article.get('id')
                summary = article.xpath('.//p[contains(@class, "videoPackageDescription")]')[0].text
            except:    
                details = article.xpath('following-sibling::script')[1].text
                clipId = RE_CLIPID.search(details).group(1)
                summary = RE_SUMMARY.search(details).group(1).replace("\\'", "'")
        
            oc.add(VideoClipObject(url=VIDEO_URL % (clipId, section_id), title=title, summary=summary,
                thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
    oc.add(NextPageObject(key=Callback(SectionMenu, section_title=section_title, section_id=section_id, page_num=page_num+1)))

    return oc

####################################################################################################
@route(PREFIX + '/localstations')
def LocalStations():
    oc = ObjectContainer(title2="Local")
    data = HTML.ElementFromURL(CTV_URL + '/video')
    for station in data.xpath('//div[@class="footernav"]//h2[text()="Local News"]/following-sibling::div/a'):
        url = station.get('href')
        title = station.get('title')
        oc.add(DirectoryObject(key=Callback(LocalMenu, url=url, title=title), title=title))
    for station in data.xpath('//div[@class="footernav"]//h2[text()="CTV Two"]/following-sibling::div/a'):
        url = station.get('href')
        title = "CTV Two " + station.get('title')
        oc.add(DirectoryObject(key=Callback(LocalMenu, url=url, title=title), title=title))
    return oc

####################################################################################################
@route(PREFIX + '/local')
def LocalMenu(url, title):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url + '/video')
    for section in data.xpath('//dt[contains(@class, "videoPlaylistCategories")]'):
        section_id = section.get('id')
        title = section.xpath('.//a')[0].text
        oc.add(DirectoryObject(key=Callback(SectionMenu, section_title=title, section_id=section_id, url=url), title=title))
    return oc