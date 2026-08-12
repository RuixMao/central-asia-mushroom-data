import hashlib,re
class RenderedProductAdapter:
 def __init__(self,config):self.config=config
 def render(self,url):
  try:from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
  except ImportError:return None,"render_dependency_missing"
  try:
   with sync_playwright() as p:
    browser=p.chromium.launch(headless=True);page=browser.new_page(locale="ru-RU",user_agent="Mozilla/5.0 YinhengMarketResearch/1.0")
    page.goto(url,wait_until="domcontentloaded",timeout=45000)
    try:page.wait_for_load_state("networkidle",timeout=15000)
    except PlaywrightTimeout:pass
    body=page.locator("body").inner_text(timeout=10000);html=page.content();browser.close()
   if re.search(r"captcha|верификац|подтвердите, что вы не робот",body,re.I):return None,"render_blocked"
   return (html,body),None
  except Exception:return None,"render_failed"
 def collect(self):
  rendered,error=self.render(self.config["url"])
  if error:return None,error
  html,body=rendered;row,error=self.parse_rendered(html,body)
  if error:return None,error
  return {**row,"page_fingerprint":hashlib.sha256(html.encode()).hexdigest()},None
