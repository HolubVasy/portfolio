#!/usr/bin/env python3
"""Собирает index.html портфолио из девяти дизайн-макетов (артборды 1440×900) в один файл.

Макеты лежат в design/<NN name>/<Name>.dc.html — это экспорт из дизайн-инструмента: артборд с
инлайн-стилями плюс маленький <style> в <helmet>. Их обёртка (x-dc, support.js, vendor/react*) для
сайта не нужна и не берётся. Полные истории кейсов (панели story-N) берутся из портфолио кита,
outbox/portfolio.html, вместе с их текстом; шрифты — из tools/fonts/ кита, встраиваются в файл.

    python3 build.py            # пишет index.html рядом
"""
import base64
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, "..", ".."))
DESIGN = os.path.join(HERE, "design")
KIT_HTML = os.path.join(KIT, "outbox", "portfolio.html")
FONT_DIR = os.path.join(KIT, "tools", "fonts")

PAGES = [  # (папка, якорь, подпись)
    ("01 Cover", "top", "Cover"), ("02 Profile", "p2", "Profile"), ("03 How I work", "p3", "How I work"),
    ("04 Case 1", "case-1", "Case 1"), ("05 Case 2", "case-2", "Case 2"), ("06 Case 3", "case-3", "Case 3"),
    ("07 Case 4", "case-4", "Case 4"), ("08 Career", "p8", "Career"), ("09 Contact", "contact", "Contact"),
]
EMAIL_OLD, EMAIL = "holubvasy@gmail.com", "vasili.holub@poly-mind.net"

# Правки содержимого поверх макетов: (страница, что, на что). Пустая «что» — проверка, что текста нет.
FIXES = [
    ("09 Contact", "Available from November 2026.", "Available now."),
    # Case 2 и Case 4: ряд тегов на строку длиннее, чем влезает, кнопка уходит за край. Последний тег — в историю.
    ("05 Case 2", '<span class="tag">mock JSON test data</span>', ""),
    ("07 Case 4", '<span class="tag">Oracle</span>', ""),
]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def fonts():
    """Те же файлы и диапазоны, что у кита: латиница и кириллица, Inter Tight и Onest."""
    rng = {"latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
           "cyrillic": "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"}
    css = []
    for fam, weight, base in (("Inter Tight", "500 800", "InterTight"), ("Onest", "400 600", "Onest")):
        for sub in ("latin", "cyrillic"):
            p = os.path.join(FONT_DIR, "%s-%s.woff2" % (base, sub))
            if not os.path.isfile(p):
                sys.exit("нет шрифта " + p)
            data = base64.b64encode(open(p, "rb").read()).decode("ascii")
            css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;"
                       "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}" % (fam, weight, data, rng[sub]))
    return "".join(css)


def artboard(folder):
    files = [f for f in os.listdir(os.path.join(DESIGN, folder)) if f.endswith(".dc.html")]
    assert len(files) == 1, folder
    t = read(os.path.join(DESIGN, folder, files[0]))
    style = re.search(r"<helmet>.*?<style>(.*?)</style>.*?</helmet>", t, re.S).group(1)
    body = t[t.find("</helmet>") + len("</helmet>"):t.find("</x-dc>")].strip()
    assert body.startswith('<div style="width: 1440px; height: 900px;'), folder
    for page, old, new in FIXES:
        if page == folder:
            assert body.count(old) == 1, (folder, old)
            body = body.replace(old, new)
    body = body.replace(EMAIL_OLD, EMAIL)
    # теги, которые начинаются с числа («~5,000 portal users», «140+ endpoints», «3 environments»), — масштаб, не технология
    body = re.sub(r'<span class="tag">(?=[~\d])', '<span class="tag n">', body)
    # кнопка «Full case story» ведёт на панель истории кейса из кита
    m = re.match(r"0(\d) Case (\d)", folder)
    if m:
        body = body.replace('href="#story"', 'href="#story-%s"' % m.group(2))
    return style, body


def stories():
    """Панели story-1..4 из портфолио кита: разметка готова, стиль наш."""
    t = read(KIT_HTML)
    out = []
    for n in (1, 2, 3, 4):
        i = t.find('<div class="sheet" id="story-%d"' % n)
        assert i > 0, n
        j = t.find("</article>", i)
        j = t.find("</div>", j) + len("</div>")
        out.append(t[i:j].replace(EMAIL_OLD, EMAIL))
    return "".join(out)


CSS = """
:root{--bg:#F5F1EA;--ink:#1E1C19;--t2:#57534C;--t3:#6E6A62;--acc:#B4471F;--acc2:#8F3617;--line:rgba(30,28,25,.12);--s:1}
*{box-sizing:border-box}
html{background:var(--bg);scroll-behavior:smooth;-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Onest,"Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body.lock{overflow:hidden}
a{color:var(--acc)}a:hover{color:var(--acc2)}
/* классы из макетов: один набор на все страницы (у страниц они совпадают) */
.meta{font:500 14px/1.4 Onest,sans-serif;color:var(--t3);letter-spacing:.02em}
.kick{font:600 13px/1.4 Onest,sans-serif;color:var(--acc);letter-spacing:.14em;text-transform:uppercase}
.lab{font:600 12px/1.4 Onest,sans-serif;color:var(--t3);letter-spacing:.12em;text-transform:uppercase}
.pill{display:inline-flex;align-items:center;font:600 12px/1 Onest,sans-serif;letter-spacing:.06em;text-transform:uppercase;padding:7px 11px;border-radius:999px;background:#F6E2D6;color:var(--acc2)}
/* теги крупнее макета (13–14px → 15px) и в два тона: цифры масштаба тёплые, технологии белые */
.tag{display:inline-flex;align-items:center;font:600 16px/1 Onest,sans-serif;padding:11px 15px;border-radius:999px;background:#FFF;border:1px solid var(--line);color:var(--ink)}
.tag.n{background:#F6E2D6;border-color:transparent;color:var(--acc2)}
.body{font:400 15px/1.55 Onest,sans-serif;color:var(--t2);margin:0}
.res{display:flex;flex-direction:column;padding:12px 0;border-top:1px solid rgba(143,54,23,.18)}
.resv{font:700 26px/1.1 'Inter Tight',sans-serif;letter-spacing:-.025em;color:var(--acc2)}
.resl{font:400 14px/1.4 Onest,sans-serif;color:var(--t2);margin-top:4px}
.row{display:grid;grid-template-columns:130px 24px minmax(0,1fr);column-gap:16px;padding:13px 0;border-top:1px solid var(--line)}
.per{font:500 15px/1.5 Onest,sans-serif;color:var(--t2);text-align:right;font-variant-numeric:tabular-nums}
.dot{width:10px;height:10px;border-radius:50%;background:var(--acc);margin:7px auto 0}
.ttl{font:700 19px/1.3 'Inter Tight',sans-serif;letter-spacing:-.012em}
.org{font:500 15px/1.4 Onest,sans-serif;color:var(--acc);margin-top:2px}
.dsc{font:400 15px/1.45 Onest,sans-serif;color:var(--t2);margin-top:3px}
.rec{display:flex;gap:14px;padding:14px 0;border-top:1px solid var(--line);font:400 15px/1.5 Onest,sans-serif;color:var(--ink)}
/* серый #7A756C из макетов был на границе контраста для мелких подписей: чуть темнее, дизайн тот же */
.pg [style*="color: #7A756C"]{color:var(--t3)!important}
/* Career выше холста 900px на 104px (семь строк): плотнее, без потерь текста */
#p8 .row{padding:9px 0}
#p8 .ttl{font-size:18px;line-height:1.25}
#p8 .org,#p8 .dsc{line-height:1.3;margin-top:1px}
#p8 h2{margin-bottom:12px!important}
#p8 [style*="padding-top: 86px"]{padding-top:74px!important}
#p8 .rec{padding:10px 0;line-height:1.4}
#p8 [style*="margin: 28px 0 10px"],#p8 [style*="margin: 24px 0 10px"]{margin:16px 0 6px!important}
/* Кейсы: теги крупнее макета, поэтому ряд тегов переносится на две строки рядом с кнопкой «Full case story»
   (как в макете, в одну строку с ней). Типографику макета не трогаем — ужимаются только отступы блоков,
   иначе страница выходит за холст 900px */
.pg[id^=case] [style*="justify-content: space-between; align-items: center; gap: 24px"]{padding-top:14px!important}
.pg[id^=case] [style*="padding-top: 36px"]{padding-top:22px!important}
.pg[id^=case] [style*="gap: 22px"]{gap:14px!important}
.pg[id^=case] [style*="padding: 14px 0"]{padding:10px 0!important}
.pg[id^=case] .res{padding:9px 0}
.pg[id^=case] [style*="padding: 22px 26px"],.pg[id^=case] [style*="padding: 20px 26px"]{padding:18px 26px!important}
.pg[id^=case] .body{line-height:1.48}
/* Case 2 и Case 4 — самые длинные: им нужен ещё один шаг уплотнения, чтобы теги в две строки поместились */
#case-2 h2,#case-4 h2{font-size:37px!important;line-height:1.08!important}
#case-2 [style*="font: 500 20px/1.45"],#case-4 [style*="font: 500 20px/1.45"]{font-size:19px!important;line-height:1.4!important}
#case-2 .body,#case-4 .body{font-size:14.5px;line-height:1.45}
#case-2 .res,#case-4 .res{padding:7px 0}
#case-2 [style*="padding: 22px 26px"],#case-4 [style*="padding: 22px 26px"],#case-2 [style*="padding: 20px 26px"],#case-4 [style*="padding: 20px 26px"]{padding:15px 24px!important}

/* разворот: холст 1440×900, масштаб под окно; на узком экране — колонка с масштабом по ширине */
.pg{position:relative;width:100%;height:calc(900px * var(--s));overflow:hidden;scroll-snap-align:start}
.pg>div{transform:scale(var(--s));transform-origin:0 0;margin:0 auto}
.pg>div{position:absolute;left:50%;top:0;margin-left:calc(-720px * var(--s))}
main{scroll-snap-type:y proximity}

/* шапка и точки, как в портфолио кита */
/* у макетов своя подпись сверху и снизу каждой страницы; плавающая шапка — только счётчик и PDF, внизу справа, чтобы не накрывать её */
/* плавающие элементы живут в правом поле макета (у артборда отступ 112px), чтобы не накрывать подпись и номер страницы */
.nav{position:fixed;z-index:40;bottom:14px;right:8px;display:flex;gap:8px;align-items:center;pointer-events:none}
.nav button{padding:9px 13px;font-size:13px}
.nav>*{pointer-events:auto}
#cur{display:none}
@media (max-width:899px),(orientation:portrait){#cur{display:inline-flex}}
.chipn{display:inline-flex;align-items:center;gap:10px;padding:10px 16px;border-radius:999px;background:rgba(255,255,255,.72);border:1px solid var(--line);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font:600 14px/1 Onest,sans-serif;color:var(--ink);text-decoration:none;cursor:pointer}
.chipn i{width:8px;height:8px;border-radius:50%;background:var(--acc);box-shadow:0 0 0 4px rgba(180,71,31,.2)}
.chipn .cnt{font-weight:500;color:var(--t3)}.chipn .cnt b{color:var(--ink);font-weight:600}
.nr{display:flex;gap:8px}
.rail{position:fixed;z-index:40;right:18px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:10px}
.rail a{position:relative;width:8px;height:8px;border-radius:50%;background:rgba(30,28,25,.22);transition:background .2s,transform .2s}
.rail a.on{background:var(--acc);transform:scale(1.35)}
.rail a span{position:absolute;right:18px;top:50%;transform:translateY(-50%);white-space:nowrap;font:500 12px/1 Onest,sans-serif;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:6px;padding:6px 9px;opacity:0;pointer-events:none;transition:opacity .15s}
.rail a:hover span{opacity:1}
.prg{position:fixed;z-index:41;top:0;left:0;height:3px;width:100%;transform-origin:0 50%;transform:scaleX(var(--p,0));background:var(--acc)}

/* полная история кейса — панель поверх страницы */
.sheet{position:fixed;inset:0;z-index:60;display:none;background:rgba(30,28,25,.45);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.sheet:target,.sheet.open{display:block}
.sheet .sx{position:absolute;inset:0}
.sp{position:absolute;right:0;top:0;bottom:0;width:min(760px,100%);overflow:auto;background:#FBF9F5;color:var(--ink);padding:36px 48px 64px;box-shadow:-24px 0 60px rgba(30,28,25,.18)}
.shd{display:flex;justify-content:space-between;align-items:center;font:500 13px/1 Onest,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);margin-bottom:28px}
.shd b{color:var(--acc);font-weight:600}
.shd .cl{font:600 14px/1 Onest,sans-serif;letter-spacing:0;text-transform:none;color:var(--ink);text-decoration:none;padding:10px 14px;border:1px solid var(--line);border-radius:999px;background:#fff}
.sp h2{margin:0;font:700 34px/1.12 'Inter Tight',sans-serif;letter-spacing:-.025em}
.sp .lead{font:500 19px/1.45 'Inter Tight',sans-serif;letter-spacing:-.01em;color:var(--ink);margin:16px 0 24px}
.sp dl{display:grid;grid-template-columns:110px minmax(0,1fr);gap:8px 20px;margin:0 0 28px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:14px;line-height:1.5}
.sp dt{font:600 12px/1.6 Onest,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--t3)}
.sp dd{margin:0;color:var(--t2)}
.sp h3{margin:28px 0 8px;font:600 13px/1.4 Onest,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--acc)}
.sp p,.sp li{font:400 16px/1.6 Onest,sans-serif;color:var(--t2);margin:0 0 10px}
.sp ul{padding-left:20px;margin:0 0 10px}
.sp b{color:var(--ink)}
.sp table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0 12px}
.sp td,.sp th{text-align:left;padding:8px 10px 8px 0;border-top:1px solid var(--line);vertical-align:top;color:var(--t2)}
.sp th{color:var(--ink);font-weight:600}

@media (max-width:899px),(orientation:portrait){
  .rail{display:none}
  .nav{left:10px;right:10px;top:10px}
  .sp{padding:24px 20px 48px}
}
@media print{
  .nav,.rail,.prg,.sheet{display:none!important}
  html,body{background:#fff}
  .pg{height:900px;page-break-after:always;overflow:visible}
  .pg>div{transform:none;position:static;margin:0 auto}
}
"""

JS = r"""
(function(){
var d=document,de=d.documentElement,pgs=[].slice.call(d.querySelectorAll(".pg")),cur=0;
function scale(){var w=document.documentElement.clientWidth,narrow=w<900||innerHeight>w;de.style.setProperty("--s",narrow?w/1440:Math.min(w/1440,innerHeight/900))}
var nl=d.getElementById("nl"),nc=d.getElementById("nc"),dots=[].slice.call(d.querySelectorAll(".rail a"));
function upd(){var y=innerHeight*.45;pgs.forEach(function(p,i){var r=p.getBoundingClientRect();if(r.top<=y&&r.bottom>y)cur=i});
 if(nl)nl.textContent=pgs[cur].getAttribute("data-label")||"";if(nc)nc.textContent=(cur<9?"0":"")+(cur+1);
 dots.forEach(function(a,i){a.classList.toggle("on",i===cur)});var h=de.scrollHeight-innerHeight;de.style.setProperty("--p",h>0?scrollY/h:0)}
function go(i){i=Math.max(0,Math.min(pgs.length-1,i));pgs[i].scrollIntoView({behavior:matchMedia("(prefers-reduced-motion:reduce)").matches?"auto":"smooth",block:"start"})}
function lay(){scale();upd()}
addEventListener("scroll",upd,{passive:true});addEventListener("resize",lay);lay();
if(d.fonts&&d.fonts.ready)d.fonts.ready.then(lay);addEventListener("load",lay);
var open=null,opener=null;
function shut(){if(open){open.classList.remove("open");d.body.classList.remove("lock");var b=open.getAttribute("data-back"),o=opener;open=null;opener=null;
 if(location.hash.indexOf("#story-")===0&&history.replaceState)history.replaceState(null,"",b);if(o&&o.focus&&d.contains(o))o.focus({preventScroll:true})}}
function show(id){var s=d.getElementById(id);if(!s)return;var from=d.activeElement;shut();opener=from&&from!==d.body?from:null;open=s;s.classList.add("open");d.body.classList.add("lock");var c=s.querySelector(".cl");if(c)c.focus({preventScroll:true})}
d.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a");if(!a)return;var h=a.getAttribute("href")||"";
 if(h.indexOf("#story-")===0){e.preventDefault();show(h.slice(1))}else if(a.classList.contains("cl")||a.classList.contains("sx")){e.preventDefault();shut()}});
if(location.hash.indexOf("#story-")===0)show(location.hash.slice(1));
addEventListener("keydown",function(e){if(e.key==="Escape"){shut();return}
 if(open&&e.key==="Tab"){var f=[].slice.call(open.querySelectorAll("a[href],button")).filter(function(x){return x.getAttribute("tabindex")!=="-1"&&x.offsetParent!==null});
  if(f.length){var i=f.indexOf(d.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()}else if(!e.shiftKey&&(i<0||i===f.length-1)){e.preventDefault();f[0].focus()}}return}
 if(open||e.metaKey||e.ctrlKey||e.altKey)return;var t=e.target.tagName;if(t==="INPUT"||t==="TEXTAREA")return;var k=e.key;
 if(k==="ArrowDown"||k==="ArrowRight"||k==="PageDown"||(k===" "&&!e.shiftKey)){e.preventDefault();go(cur+1)}
 else if(k==="ArrowUp"||k==="ArrowLeft"||k==="PageUp"||(k===" "&&e.shiftKey)){e.preventDefault();go(cur-1)}
 else if(k==="Home"){e.preventDefault();go(0)}else if(k==="End"){e.preventDefault();go(pgs.length-1)}});
})();
"""


def main():
    pages, styles = [], []
    for folder, anchor, label in PAGES:
        style, body = artboard(folder)
        styles.append(style)
        pages.append('<section class="pg" id="%s" data-label="%s">%s</section>' % (anchor, html.escape(label), body))
    rail = "".join('<a href="#%s"%s><span>%02d · %s</span></a>' % (a, ' class="on"' if i == 0 else "", i + 1, l)
                   for i, (_, a, l) in enumerate(PAGES))
    desc = "Senior .NET Developer in Poznań, Poland. Four cases: integration without downtime, 140+ endpoints off in-memory caches, Grafana dashboards shipped with services, a customs system that earned a state medal."
    out = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
           "<title>Vasili Holub · Portfolio</title>\n<meta name=\"description\" content=\"%s\">\n"
           "<meta property=\"og:title\" content=\"Vasili Holub · Senior .NET Developer\">\n<meta property=\"og:description\" content=\"%s\">\n"
           "<link rel=\"icon\" href=\"data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%%3E%%3Crect width='64' height='64' rx='14' fill='%%23B4471F'/%%3E%%3Ctext x='32' y='42' font-family='Inter Tight,Arial,sans-serif' font-size='28' font-weight='700' fill='white' text-anchor='middle'%%3EVH%%3C/text%%3E%%3C/svg%%3E\">\n"
           "<style>%s</style>\n<style>%s</style>\n</head>\n<body>\n"
           "<div class=\"prg\" aria-hidden=\"true\"></div>\n"
           "<header class=\"nav\"><span class=\"chipn\" id=\"cur\"><span class=\"lab\" id=\"nl\">Cover</span><span class=\"cnt\"><b id=\"nc\">01</b> / 09</span></span><button class=\"chipn\" type=\"button\" onclick=\"window.print()\" title=\"Save as PDF\">PDF</button></header>\n"
           "<nav class=\"rail\" aria-label=\"Pages\">%s</nav>\n<main>\n%s\n</main>\n%s\n<script>%s</script>\n</body>\n</html>\n"
           ) % (html.escape(desc), html.escape(desc), fonts(), CSS, rail, "\n".join(pages), stories(), JS)
    out_path = os.path.join(HERE, "index.html")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("index.html: %d KB, pages %d" % (len(out.encode("utf-8")) // 1024, len(pages)))


if __name__ == "__main__":
    main()
