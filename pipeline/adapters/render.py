import hashlib,re
from urllib.parse import quote,urlsplit,urlunsplit
def _normalize_url(url):
 """非 ASCII URL 规范化：path/query 中的本地语言字符自动百分号编码。
 Playwright 的 page.goto 对未编码的西里尔/本地语言字符直接抛异常 → render_failed
 （1 秒内失败，非 45s 超时）。适配器配置里的 URL 可能含 грибы 等原文。"""
 try:
  parts=urlsplit(url)
  if not parts.scheme:return url
  path=quote(parts.path,safe="/%:@=")
  query=quote(parts.query,safe="=&%+/?~")
  return urlunsplit((parts.scheme,parts.netloc,path,query,parts.fragment))
 except Exception:return url
class RenderedProductAdapter:
 def __init__(self,config):self.config=config
 def render(self,url):
  try:from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
  except ImportError:return None,"render_dependency_missing"
  try:
   url=_normalize_url(url)
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
  return {**row,"source_type":"rendered","page_fingerprint":hashlib.sha256(html.encode()).hexdigest()},None
 def collect_many(self):
  """多商品采集：默认单条；子类覆写 parse_rendered_many 后自动返回多条。"""
  if self.__class__.parse_rendered_many is RenderedProductAdapter.parse_rendered_many:
   row,error=self.collect()
   if error:return [],error
   return [row],None
  rendered,error=self.render(self.config["url"])
  if error:return [],error
  html,body=rendered;rows=self.parse_rendered_many(html,body)
  if not rows:return [],"price_missing"
  fp=hashlib.sha256(html.encode()).hexdigest()
  return [{**row,"source_type":"rendered","page_fingerprint":fp} for row in rows],None
 def parse_rendered_many(self,html,body=""):
  """子类可覆写为返回多条商品；基类默认只解析第一条。"""
  row,error=self.parse_rendered(html,body)
  if error:return []
  return [row]
