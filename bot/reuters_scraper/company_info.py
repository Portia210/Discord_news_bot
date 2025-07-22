import requests
from bs4 import BeautifulSoup
import asyncio
import concurrent.futures

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en,en-US;q=0.9,he;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'cookie': '_ga_WBSR7WLTGD=GS2.1.s1753114952$o2$g1$t1753117258$j60$l0$h0; _ga_WBSR7WLTGD=GS2.1.s1753114952$o2$g1$t1753114980$j32$l0$h0; _pbjs_userid_consent_data=3524755945110770; usprivacy=1---; permutive-id=b630fb2e-3c1a-470f-8baa-c8796caa490d; _gcl_au=1.1.1031266329.1751480583; _cb=DDUf58B8-ooACdIzCD; _v__chartbeat3=BDMp4ND9SFl_CWgl2Z; ajs_anonymous_id=70cb261e-ab99-4e34-8155-4b4c166b3db8; _cc_id=310888c5665f3d46a138382117008fad; _ga=GA1.2.1998790357.1751480588; _ga_WBSR7WLTGD=GS2.1.s1751480588$o1$g1$t1751480664$j44$l0$h0; OneTrustWPCCPAGoogleOptOut=false; cleared-onetrust-cookies=Thu, 17 Feb 2022 19:17:07 GMT; _li_dcdm_c=.reuters.com; _lc2_fpi=f511229f0ef8--01k0pw3k68658rqm3jaa4qdn0a; _lc2_fpi_js=f511229f0ef8--01k0pw3k68658rqm3jaa4qdn0a; _fbp=fb.1.1753114342215.359723743322512753; _gid=GA1.2.799981603.1753114348; panoramaId_expiry=1753719156172; panoramaId=a93ce679f074b051895cba9ed4c116d53938f6de518a34fd802bb542342a1562; panoramaIdType=panoIndiv; BOOMR_CONSENT="opted-in"; _li_ss=CpcBCgYI-QEQphsKBgj3ARCmGwoFCAoQphsKBgikARCmGwoGCN0BEKYbCgYIgQEQphsKBQgMELAbCgYI9QEQphsKBQgLEKYbCgYIiQEQphsKBgilARCmGwoGCIACEKgbCgYI4QEQphsKBgiiARCmGwoGCP8BEKYbCgkI_____wcQsBsKBgiHAhCmGwoGCNIBEKYbCgUIfhCmGw; cto_bundle=EH2f4V8yUVBWU1prdDBKUHZpcTg3REYxSjdKaWslMkJUNDd6U3hSeDNNMUpOd2ViUjNpOXU5S0I2RmxpZWhmY2N0bm9TaWFocngwbUtCY2pjUnBDaW1JMmdWd3NyQmZsWDJUNjRrNEN6bjJNcVhmUklqJTJCTk9rOHN0SEJ2SUF5MWVWRnNUMElxOXREOWFaR2dNa3JZUm0lMkIzUVVBQ0ElM0QlM0Q; __gads=ID=8c3e5069d1a0bd11:T=1753114356:RT=1753116943:S=ALNI_MYfBo8LVZNbhVEZzFT0Lm9nQSQryg; __eoi=ID=9a0dbe29efb947ac:T=1753114357:RT=1753116943:S=AA-AfjbHKSaN5dgT6ujIcnD09Aq1; bounceClientVisit5431v=N4IgNgDiBcIBYBcEQM4FIDMBBNAmAYnvgO6kB0ATgKYCuCVFKZAxgPYC2R7AhhQNZUE6Am3YRuAOwCWVYfixYACgBkyAeQCKIADQgKMECAC+QA; ABTasty=uid=9sbykwnwjf2vmzxf; ABTastySession=mrasn=&lp=https%253A%252F%252Fwww.reuters.com%252Fmarkets%252Fcompanies%252FIREN.OQ; OptanonConsent=groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&datestamp=Mon+Jul+21+2025+19%3A55%3A58+GMT%2B0300+(%D7%A9%D7%A2%D7%95%D7%9F+%D7%99%D7%A9%D7%A8%D7%90%D7%9C+(%D7%A7%D7%99%D7%A5))&version=202505.2.0&hosts=&isGpcEnabled=0&browserGpcFlag=0&isIABGlobal=false&consentId=ac3ba626-9d18-4945-bd8d-16291ec11314&interactionCount=0&isAnonUser=1&landingPath=NotLandingPage&AwaitingReconsent=false; reuters-geo={"country":"-", "region":"-"}; _awl=2.1753116959.5-0ed1e39ec205942418e2d1b5004d8049-6763652d6575726f70652d7765737431-1; _chartbeat2=.1751480586091.1753116960960.0000010000000001.OYe96BZd8iuCyPnofhs6bBCrOvuC.1; _cb_svref=external; _ga_XYG3C0S56N=GS2.2.s1753116617$o3$g1$t1753116965$j60$l0$h0; datadome=MDCzqKTulTks63VKUMpcGeeTdRL9UwFrOPD4pjQNaX8zXDtZjKtnQDZgLr1nIHefI_czx7JrKxQHBxlSPhr3lgtrq1mjiKH1eWTIGwEZM0cChemYBgyAdF__gW34m8gk; _gat=1; _dd_s=rum=0&expire=1753118160623; RT="z=1&dm=www.reuters.com&si=12cf9c08-71e9-4239-8862-60cbe8e352f0&ss=mddcco4a&sl=5&tt=3w3&obo=4&rl=1&ld=ei0n&r=2uljynzh&ul=ei0n"',
}


# Create a session for consistent requests
session = requests.Session()
session.headers.update(headers)

def get_description(symbol):
    response = session.get(f"https://www.reuters.com/markets/companies/{symbol}.OQ")
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    soup = BeautifulSoup(response.text, 'html.parser')
    description = soup.find("p", class_="about-company-card__description__2DHYt")
    if description:
        return description.text
    else:
        return None

async def get_description_async(symbol):
    # Add a small delay to avoid rate limiting
    await asyncio.sleep(0.5)
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, get_description, symbol)

async def get_companies_description(companies_symbols):
    tasks = []
    for symbol in companies_symbols:
        tasks.append(get_description_async(symbol))
    
    descriptions = await asyncio.gather(*tasks)
    # Filter out None values
    valid_descriptions = [desc for desc in descriptions if desc is not None]
    print(f"Total descriptions: {len(descriptions)}, Valid descriptions: {len(valid_descriptions)}")
    return valid_descriptions


if __name__ == "__main__":
    # Test with requests (asynchronous using thread pool)
    print("\n=== REQUESTS ASYNC ===")
    companies_symbols = ["AAPL", "MSFT", "GOOGL", "PLTR", "IREN"]
    descriptions_async = asyncio.run(get_companies_description(companies_symbols))