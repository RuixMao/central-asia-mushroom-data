"""Uzum.uz(乌兹别克斯坦最大电商)适配器。

实测结论(2026-08-18,CI ubuntu-latest + 渲染验证):
  - Uzum 全站对数据中心出口 IP(本地与 GitHub Actions)均返回验证码页:
    body 为 "Подтвердите, что запросы отправляли вы, а не робот"
  - 渲染成功(html 15KB),但页面无商品数据;API(api.uzum.uz)返回 403/404 封闭
  - 结论:公开通道被反爬完全封闭,符合"不绕过验证码"约束 → 保持 render_blocked
  - 适配器代码/解析逻辑(商品卡+сум 价格+稳定 ID)已就绪,待住宅 IP/官方 API 开放后启用

策略(遵循"不绕过验证码"约束):
  - 渲染后检测验证码(含 Uzum 实际句式)→ 返回 render_blocked,不尝试破解
  - 渲染成功后按商品卡片解析标题 + сум 价格 + 稳定商品 ID
  - 无结果/被拦截一律返回明确 gap,不写 0 元或虚构价格
  - UZUM_DEBUG=1 时打印渲染页片段(诊断商品卡选择器)
"""
import hashlib
import os
import re

from bs4 import BeautifulSoup

from .render import RenderedProductAdapter

UZS_PRICE = re.compile(r"(\d[\d\s,.]{1,15})\s*(?:сум|UZS)", re.I)
# Uzum 实际验证码句式:"Подтвердите, что запросы отправляли вы, а не робот"
CAPTCHA = re.compile(
    r"captcha|проверка|подтвердите, что вы не робот|запросы отправляли вы|а не робот",
    re.I,
)


class UzumAdapter(RenderedProductAdapter):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def collect_many(self):
        rendered, error = self.render(self.config["url"])
        if error:
            return [], error
        html, body = rendered
        # 调试:UZUM_DEBUG=1 时打印渲染页片段(诊断商品卡选择器用)
        if os.getenv("UZUM_DEBUG", "0") == "1":
            print(f"[uzum-debug] url={self.config['url']}")
            print(f"[uzum-debug] body_len={len(body or '')} html_len={len(html or '')}")
            print(f"[uzum-debug] captcha_match={bool(CAPTCHA.search(body or ''))}")
            import re as _re
            cards = _re.findall(r'(?:data-testid|class)="[^"]*(?:product|card|item)[^"]*"', html or "")
            print(f"[uzum-debug] card_markers={cards[:10]}")
            print(f"[uzum-debug] body_head={ (body or '')[:500] }")
        if CAPTCHA.search(body or ""):
            return [], "render_blocked"
        rows = self.parse_rendered_many(html, body)
        if not rows:
            return [], "price_missing"
        return rows, None

    def parse_rendered_many(self, html, body=""):
        soup = BeautifulSoup(html, "html.parser")
        rows = {}
        for card in soup.select('[data-testid="product-card"], .product-card, [data-product-id], .card-product'):
            text = " ".join(card.get_text(" ", strip=True).split())
            if not re.search(r"гриб|шампин|вешен|шиитак|эноки|эринги|qo'ziqorin|shampinyon|sampinyon", text, re.I):
                continue
            match = UZS_PRICE.search(text)
            if not match:
                continue
            price = float(match.group(1).replace(" ", "").replace(",", ""))
            if price <= 0:
                continue
            link = card.find("a", href=True)
            url = link["href"] if link else self.config["url"]
            if url.startswith("/"):
                url = "https://uzum.uz" + url
            pid_match = re.search(r"/product/(\d+)", url)
            product_id = f"uzum-{pid_match.group(1)}" if pid_match else hashlib.sha256(url.encode()).hexdigest()[:20]
            rows[product_id] = {**self.config, "platform_product_id": product_id,
                                "url": url, "original_title": text[:240],
                                "current_price": price, "raw_price_text": match.group(0),
                                "source_type": "rendered",
                                "page_fingerprint": hashlib.sha256(html.encode()).hexdigest()}
        return list(rows.values())
