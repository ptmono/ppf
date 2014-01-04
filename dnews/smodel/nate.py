

class NateBreakingNewsModel(GetSetModel):
    def set_sels(self):
        selector = ('dl[class="mduSubjectContent"]')
        sel = CSSSelector(selector)
        sel_list = sel(fromstring(self.source))
        return sel_list
        
    def getTitle(self):
        result = []
        selector = ('a strong')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            title = sel_list[0].text_content()
            result.append(title)
        return result

    def getSummary(self):
        result = []
        selector = ('dd a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            try:
                summary = sel_list[0].text_content().strip()
            except IndexError as err:
                logger().debug(sel_list)
                summary = ""
            result.append(summary)
        return result
    
    def getUrl(self):
        result = []
        selector = ('a')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            result.append(sel_list[0].get('href'))
        return result

    def getMedia(self):
        result = []
        selector = ('span[class="medium"]')
        sel_sub = CSSSelector(selector)
        for sel in self._sels:
            sel_list = sel_sub(sel)
            try:
                media = sel_list[0].text.strip()
            except IndexError as err:
                logger().debug(sel_list)
                media = ""
            result.append(media)
        return result

    def getContent(self):
        return ['' for i in range(len(self._sels))]
