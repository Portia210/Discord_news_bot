import requests
from utils.read_write import write_json_file

cookies = {
    'A3': 'd=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg',
    'GUC': 'AQABCAFoZr5olkIc-wSJ&s=AQAAAIdHtF0U&g=aGVycQ',
    'A1S': 'd=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg',
    'A1': 'd=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg',
    'tbla_id': 'e7fe438e-84c7-4cc2-917f-3b82510bda39-tuctf2f6fdb',
    'EuConsent': 'CQT7KEAQT7KEAAOACBHEBxFoAP_gAEPgACiQKptB9G7WTXFneTp2YPskOYwX0VBJ4MAwBgCBAUABzBIUIBwCVmAzJEyIICACGAIAIGBBIABtGAhAQEAAYIAFAABIAEgAIBAAIGAAACAAAABACAAAAAAAAAAQgEAXMBQgmCYEBFoIQUhAggAgAQAAAAAEAIgBCAQAEAAAQAAACAAIACgAAgAAAAAAAAAEAFAIEAAAIAECAgvkdAAAAAAAAAAIAAYACAABAAAAAIKpgAkGhUQRFgQAhEIGEECAAQUBABQIAgAACBAAAATBAUIAwAVGAiAEAIAAAAAAAAAAABAAABAAhAAEAAQIAAAAAIAAgAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAGIBAggCAABBAAQUAAAAAgAAAAAAAAAIgACAAAAAAAAAAAAAAIgAAAAAAAAAAAAAAAAAAIEAAAIAAAAoDEFgAAAAAAAAAAAAAACAABAAAAAIAAA',
    'axids': 'gam=y-ZXW.GtdE2uIcKMnJTlVCAkYz_ZrV42oj~A&dv360=eS00QXB3bmd4RTJ1Rzg5alBpbmxETG83MnRHa3JOZEdWVX5B&ydsp=y-YdyE4LNE2uKrZBVA1MkZ_6SQXDAUX2eM~A&tbla=y-YA.WjD9E2uJ5v8dqu4d6y_zxH8rziNJW~A',
    'PRF': 't%3D%255EDJI%252B%255EGSPC%252BQQQ%252BPLTR%26dock-collapsed%3Dtrue',
    'cmp': 't=1752182159&j=1&u=1---&v=88',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en,en-US;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'https://finance.yahoo.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://finance.yahoo.com/topic/stock-market-news/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'cookie': 'A3=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; GUC=AQABCAFoZr5olkIc-wSJ&s=AQAAAIdHtF0U&g=aGVycQ; A1S=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; A1=d=AQABBKGKc2cCEHT7atMqsTimn1z_h2DE9DgFEgABCAG-ZmiWaF5EyyMA9qMCAAcIdFG_ZgcRnMQ&S=AQAAAhI85Rn162FjBhJVZVHLEzg; tbla_id=e7fe438e-84c7-4cc2-917f-3b82510bda39-tuctf2f6fdb; EuConsent=CQT7KEAQT7KEAAOACBHEBxFoAP_gAEPgACiQKptB9G7WTXFneTp2YPskOYwX0VBJ4MAwBgCBAUABzBIUIBwCVmAzJEyIICACGAIAIGBBIABtGAhAQEAAYIAFAABIAEgAIBAAIGAAACAAAABACAAAAAAAAAAQgEAXMBQgmCYEBFoIQUhAggAgAQAAAAAEAIgBCAQAEAAAQAAACAAIACgAAgAAAAAAAAAEAFAIEAAAIAECAgvkdAAAAAAAAAAIAAYACAABAAAAAIKpgAkGhUQRFgQAhEIGEECAAQUBABQIAgAACBAAAATBAUIAwAVGAiAEAIAAAAAAAAAAABAAABAAhAAEAAQIAAAAAIAAgAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAGIBAggCAABBAAQUAAAAAgAAAAAAAAAIgACAAAAAAAAAAAAAAIgAAAAAAAAAAAAAAAAAAIEAAAIAAAAoDEFgAAAAAAAAAAAAAACAABAAAAAIAAA; axids=gam=y-ZXW.GtdE2uIcKMnJTlVCAkYz_ZrV42oj~A&dv360=eS00QXB3bmd4RTJ1Rzg5alBpbmxETG83MnRHa3JOZEdWVX5B&ydsp=y-YdyE4LNE2uKrZBVA1MkZ_6SQXDAUX2eM~A&tbla=y-YA.WjD9E2uJ5v8dqu4d6y_zxH8rziNJW~A; PRF=t%3D%255EDJI%252B%255EGSPC%252BQQQ%252BPLTR%26dock-collapsed%3Dtrue; cmp=t=1752182159&j=1&u=1---&v=88',
}

params = {
    'location': 'US',
    'queryRef': 'topicsDetailFeed',
    'serviceKey': 'ncp_fin',
    'lang': 'en-US',
    'region': 'US',
}

data = '{"serviceConfig":{"snippetCount":50,"count":250,"imageTags":["559x314|1|80","559x314|2|80","365x205|1|80","365x205|2|80","168x126|1|80","168x126|2|80"],"listId":"530aec16-61ed-4c8e-8fd8-f60d01bd0722","spaceId":"1183308065","rid":"06spi0lk70bcb"},"session":{"consent":{"allowContentPersonalization":true,"allowCrossDeviceMapping":true,"allowFirstPartyAds":true,"allowSellPersonalInfo":true,"canEmbedThirdPartyContent":true,"canSell":true,"consentedVendors":["acast","brightcove","dailymotion","facebook","flourish","giphy","instagram","nbcuniversal","playbuzz","scribblelive","soundcloud","tiktok","vimeo","twitter","youtube","masque"],"allowAds":true,"allowOnlyLimitedAds":false,"rejectedAllConsent":false,"allowOnlyNonPersonalizedAds":false},"authed":"0","ynet":"0","ssl":"1","spdy":"0","ytee":"0","mode":"normal","tpConsent":true,"site":"finance","adblock":"0","bucket":["transmit-prebid-ssai-ctrl-2","addensitylevers-test","april2024Prices"],"colo":"ir2","device":"desktop","bot":"0","browser":"chrome","app":"unknown","ecma":"modern","environment":"prod","gdpr":true,"lang":"en-US","dir":"ltr","intl":"us","network":"broadband","os":"windows nt","partner":"none","region":"US","time":1752182155478,"tz":"Asia/Jerusalem","usercountry":"IL","rmp":"0","webview":"0","feature":["awsCds","disableInterstitialUpsells","disableServiceRewrite","disableBack2Classic","disableYPFTaxArticleDisclosure","enable1PVideoTranscript","enableAdRefresh20s","enableAnalystRatings","enableAPIRedisCaching","enableArticleRecommendedVideoInsertion","enableArticleRecommendedVideoInsertionTier34","enableCGAuthorFeed","enableChartbeat","enableChatSupport","enableCommunityForYouFeed","enableCommunityLoggedOutView","enableCompare","enableContentOfferVertical","enableCompareConvertCurrency","enableConsentAndGTM","enableFeatureEngagementSystem","enableCrumbRefresh","enableCSN","enableCurrencyConverter","enableDarkMode","enableDockAddToFollowing","enableDockPortfolioControl","enableExperimentalDockModules","enableFollow","enableEntityDiscover","enableEntityDiscoverInStream","enableFollowTopic","enableHistoricalStockPicks","enableLazyQSP","enableLiveBlogStatus","enableLivePage","enableLSEGTopics","enableStreamingNowBar","enableLocalSpotIM","enableMarketsLeafHeatMap","enableMultiQuote","enableMyMoneyOptIn","enableNeoBasicPFs","enableNeoGreen","enableNeoHouseCalcPage","enableNeoInvestmentIdea","enableNeoMortgageCalcPage","enableNeoQSPReportsLeaf","enableNeoResearchReport","enableOffPeakPortalAds","enableOffPeakDockAds","enableOvernight","enablePersonalFinanceArticleReadMoreAlgo","enablePersonalFinanceNavBar","enablePersonalFinanceNewsletterIntegration","enablePersonalFinanceZillowIntegration","enablePfPremium","enablePfStreaming","enablePinholeScreenshotOGForQuote","enablePlus","enablePortalStockStory","enablePrivateCompany","enablePrivateCompanySurvey","enableQSP1PNews","enableQSPChartEarnings","enableQSPChartNewShading","enableQSPChartRangeTooltips","enableQSPCommunity","enableQSPEarnings","enableQSPEarningsVsRev","enableQSPHistoryPlusDownload","enableQSPLiveEarnings","enableQSPLiveEarningsCache","enableQSPLiveEarningsFeatureCue","enableQSPLiveEarningsIntl","enableQSPHoldingsCard","enableQSPNavIcon","enableQSPStockPicks","enableQSPStockPicksMF","enableQuoteLookup","enableRecentQuotes","enableResearchHub","enableScreenerCustomColumns","enableScreenerHeatMap","enableScreenersCollapseDock","enableScreenersSpEarnings","enableScreenersIndex","enableSECFiling","enableSigninBeforeCheckout","enableSmartAssetMsgA","enableStockStoryPfPage","enableStreamOnlyNews","enableTradeNow","enableUpgradeBadgeDesign","enableYPFArticleReadMoreAll","enableVideoInHero","enableDockQuoteEventsModule","enablePfDetailDockCollapse","enablePfPrivateCompany","enableHoneyLinks","partnerAARP","enableFollowedLatestNews","enableCGFollowedLatestNews","enableStockPicks","enableStockPicksProduction","enableDockModuleDescriptions","enableSimpleHeaderCheckout","enableDockFooterSettings","enableCompareFeatures","enableGenericHeatMap","enableQSPIndustryHeatmap","enableStatusBadge","enableOffPeakArticleInBodyAds"],"isDebug":false,"isForScreenshot":false,"isWebview":false,"theme":"auto","pnrID":"","isError":false,"gucJurisdiction":"IL","areAdsEnabled":true,"ccpa":{"warning":"","footerSequence":["terms_and_privacy","privacy_settings"],"links":{"privacy_settings":{"url":"https://guce.yahoo.com/privacy-settings?locale=en-US","label":"Privacy & Cookie Settings","id":"privacy-link-privacy-settings"},"terms_and_privacy":{"multiurl":true,"label":"${terms_link}Terms${end_link} and ${privacy_link}Privacy Policy${end_link}","urls":{"terms_link":"https://guce.yahoo.com/terms?locale=en-US","privacy_link":"https://guce.yahoo.com/privacy-policy?locale=en-US"},"ids":{"terms_link":"privacy-link-terms-link","privacy_link":"privacy-link-privacy-link"}}}},"yrid":"06spi0lk70bcb","user":{"age":-2147483648,"crumb":"X7OMi/Fe4nm","firstName":null,"gender":"","year":0}}}'

response = requests.post('https://finance.yahoo.com/xhr/ncp', params=params, headers=headers, data=data)

response.raise_for_status()

if response.status_code == 200:
    print("success")
    write_json_file("yf_scraper/responses/news.json", response.json())
    stream = response.json()["data"]["main"]["stream"]
    for item in stream:
        print(item["content"]["title"], "\n", item["content"]["story"], "--------------------------------")
