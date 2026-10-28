# -*- coding: utf-8 -*-
"""
GOLDEN-EYE 源巡检 · 通用探测库（输入驱动，仅用标准库）。

支持两种源类型：
  - vod_api : Apple CMS 采集接口（形如 https://x.com/api.php/provide/vod）
              探测「能否搜索 + 是否返回 m3u8 播放地址」
  - m3u8    : 直播 / HLS 播放列表地址
              探测「是否可达 + 是否为合法播放列表」

核心原则：要探测的 URL 永远由调用方传入（来自请求体 / 配置文件），
本库不内置任何源池。这样无论源是否授权，探测能力本身都是中立、合规的技术工具。
"""
import ipaddress
import json
import os
import socket
import ssl
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

# SSRF 防护：本服务会按调用方传入的 URL 发起请求，若不加限制，
# 托管到公网后可能被利用去读取服务器本地文件、探测内网或云元数据。
# 默认只允许公网 http/https；私有地址探测属合法需求时，
# 可设 ALLOW_PRIVATE_TARGETS=1 显式开启。
ALLOW_PRIVATE = os.environ.get("ALLOW_PRIVATE_TARGETS", "").strip() in ("1", "true", "yes")
MAX_WORKERS = 32

# 很多源站用自签/过期证书；探测目的是"能不能播"，不是"证书是否正规"
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def _blocked_reason(url):
    """返回 None 表示允许探测；否则返回被拦截的原因说明。

    拦截规则：
      1. 只放行 http / https（挡住 file://、ftp:// 等本地/非常规协议）
      2. 默认拦掉私有 / 回环 / 链路本地地址（挡住内网与云元数据 169.254.169.254）
    """
    try:
        parts = urllib.parse.urlparse(url)
    except Exception:
        return "URL 无法解析"

    scheme = (parts.scheme or "").lower()
    if scheme not in ("http", "https"):
        return "仅支持 http/https 地址（收到 %s://）" % (scheme or "空")

    if ALLOW_PRIVATE:
        return None

    host = parts.hostname
    if not host:
        return "缺少主机名"

    # 直接是 IP 字面量的情况
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None

    if ip is not None:
        if _is_private_ip(ip):
            return "默认不探测私有地址 %s（如需探测内网源，请设 ALLOW_PRIVATE_TARGETS=1）" % ip
        return None

    # 域名：解析后逐个检查，挡住指向内网的域名
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return "域名解析失败"
    for info in infos:
        try:
            candidate = ipaddress.ip_address(info[4][0])
        except Exception:
            continue
        if _is_private_ip(candidate):
            return "域名 %s 解析到私有地址 %s（默认不探测内网，如需请设 ALLOW_PRIVATE_TARGETS=1）" % (host, candidate)
    return None


def _is_private_ip(ip):
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _maybe_blocked(name, url, kind):
    """先做安全策略检查；被拦截则返回 BLOCKED 结果，否则返回 None 继续探测。"""
    reason = _blocked_reason(url)
    if reason:
        return {"name": name, "url": url, "kind": kind, "status": "BLOCKED",
                "ms": 0, "detail": reason}
    return None


def _http_get(url, timeout=15, max_bytes=400000):
    """返回 (耗时ms, 原始bytes 或 错误str)。直连，绕过本机代理。"""
    reason = _blocked_reason(url)
    if reason:
        return 0, "BLOCKED: " + reason
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=SSL_CTX),
    )
    t0 = time.time()
    try:
        data = opener.open(req, timeout=timeout).read(max_bytes)
        return int((time.time() - t0) * 1000), data
    except Exception as e:  # noqa: BLE001 - 探测本身就是看异常
        return int((time.time() - t0) * 1000), str(e)[:160]


def probe_vod_api(base, keyword="test", timeout=15):
    blocked = _maybe_blocked(base, base, "vod_api")
    if blocked:
        return blocked
    url = base.rstrip("/") + "/?ac=videolist&pg=1&wd=" + urllib.parse.quote(keyword)
    ms, payload = _http_get(url, timeout)
    if not isinstance(payload, bytes):
        return {"name": base, "url": base, "kind": "vod_api", "status": "ERR",
                "ms": ms, "m3u8": 0, "detail": payload[:80]}
    try:
        data = json.loads(payload.decode("utf-8", "ignore"))
    except Exception:
        return {"name": base, "url": base, "kind": "vod_api", "status": "BAD_JSON",
                "ms": ms, "m3u8": 0, "detail": payload[:80].decode("utf-8", "ignore")}
    lst = data.get("list") or []
    if not isinstance(lst, list) or not lst:
        return {"name": base, "url": base, "kind": "vod_api", "status": "EMPTY",
                "ms": ms, "m3u8": 0, "detail": "total=%s" % data.get("total")}
    m3u8 = sum(1 for it in lst if ".m3u8" in (it.get("vod_play_url") or ""))
    return {"name": base, "url": base, "kind": "vod_api",
            "status": "GOOD" if m3u8 else "NO_M3U8", "ms": ms, "m3u8": m3u8,
            "detail": "list=%d m3u8=%d" % (len(lst), m3u8)}


def probe_m3u8(url, timeout=15):
    blocked = _maybe_blocked(url, url, "m3u8")
    if blocked:
        return blocked
    ms, payload = _http_get(url, timeout, max_bytes=200000)
    text = payload.decode("utf-8", "ignore") if isinstance(payload, bytes) else payload
    if isinstance(text, str):
        if "#EXTM3U" in text or "#EXTINF" in text:
            lines = [l for l in text.splitlines() if l and not l.startswith("#")]
            return {"name": url, "url": url, "kind": "m3u8", "status": "GOOD",
                    "ms": ms, "segments": len(lines), "detail": "playlist ok"}
        if text[:1] == "{":
            return {"name": url, "url": url, "kind": "m3u8", "status": "BAD_JSON",
                    "ms": ms, "detail": text[:80]}
        low = text.lower()
        if "<!doctype" in low or "<html" in low:
            return {"name": url, "url": url, "kind": "m3u8", "status": "NOT_PLAYLIST",
                    "ms": ms, "detail": "returned html"}
    return {"name": url, "url": url, "kind": "m3u8", "status": "ERR",
            "ms": ms, "detail": (text[:80] if isinstance(text, str) else str(text))[:80]}


def probe_one(item):
    """item: {"name":..., "url":..., "kind": "vod_api"|"m3u8"|"auto", "keyword":...}"""
    name = item.get("name", item.get("url", "?"))
    url = item.get("url")
    if not url:
        return {"name": name, "url": "", "status": "NO_URL", "ms": 0, "detail": "missing url"}
    kind = item.get("kind", "auto")
    if kind == "auto":
        kind = "vod_api" if "provide/vod" in url else "m3u8"
    if kind == "vod_api":
        return probe_vod_api(url, item.get("keyword", "test"))
    return probe_m3u8(url)


def probe_batch(items, workers=8):
    if not isinstance(items, list):
        return [{"name": "?", "url": "", "status": "ERR", "ms": 0,
                 "detail": "items 必须是数组"}]
    items = [it for it in items if isinstance(it, dict)]
    if not items:
        return []
    # 限制并发上限，避免传入超大 workers 时瞬间开满线程拖垮服务
    try:
        workers = int(workers)
    except (TypeError, ValueError):
        workers = 8
    workers = max(1, min(workers, MAX_WORKERS, len(items)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(probe_one, items))


if __name__ == "__main__":
    import sys
    sample = [{"name": "demo",
               "url": sys.argv[1] if len(sys.argv) > 1 else "https://example.com/api.php/provide/vod"}]
    print(json.dumps(probe_batch(sample), ensure_ascii=False, indent=2))
