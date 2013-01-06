RE_CLIPID   = Regex('clip.id = ([0-9]+)')
RE_SUMMARY  = Regex('clip.description = "(.+)";')

PREFIX          = '/video/ctvnews'
NAME            = 'CTV News'
CTV_URL         = 'http://www.ctvnews.ca/video'
VIDEO_URL       = 'http://www.ctvnews.ca/video?clipId=%s&binId=%s'
PLAYLIST_URL    = "http://www.ctvnews.ca/%s?ot=example.AjaxPageLayout.ot&pageNum=%d&maxItemsPerPage=12"

ART     = 'art-default.jpg'
ICON    = 'icon-default.png'

####################################################################################################
def Start():
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'CTV News'

    DirectoryObject.thumb = R(ICON)

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():
    oc = ObjectContainer()
    data = HTML.ElementFromURL(CTV_URL)
    for section in data.xpath('//dt[contains(@class, "videoPlaylistCategories")]'):
        section_id = section.get('id')
        title = section.xpath('.//a')[0].text
        oc.add(DirectoryObject(key=Callback(SectionMenu, section_title=title, section_id=section_id), title=title))
    return oc

####################################################################################################
@route(PREFIX + '/section/{section_title}/{section_id}/{page_num}', page_num=int)
def SectionMenu(section_title, section_id, page_num=1):
    oc = ObjectContainer(title2=section_title)
    data = HTML.ElementFromURL(PLAYLIST_URL % section_id, page_num)
    for article in data.xpath('//article'):
        title = article.xpath('.//p[@class="videoPlaylistDescription"]')[0].text
        thumb = article.xpath('.//img')[0].get('src').replace('box_180', 'landscape_960')
        details = article.xpath('following-sibling::script')[1].text
        clipId = RE_CLIPID.search(details).group(1)
        summary = RE_SUMMARY.search(details).group(1)
        oc.add(VideoClipObject(url=VIDEO_URL % (clipId, section_id), title=title, summary=summary,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
    oc.add(NextPageObject(key=Callback(SectionMenu, section_title, section_id, page_num=page_num+1)))
    return oc
