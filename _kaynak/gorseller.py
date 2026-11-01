"""veri.json'dan dört proje görseli (HTML -> Brave headless -> assets/proje/*.png).
Sayılar Kırak Metal verisinin gerçek toplamları; görünüm Power BI / SSMS / Excel ekranına benzer."""
import json, subprocess, html
from pathlib import Path

KOK = Path(__file__).resolve().parent
V = json.loads((KOK / "veri.json").read_text(encoding="utf-8"))
CIKTI = KOK.parent / "assets" / "proje"
CIKTI.mkdir(parents=True, exist_ok=True)
BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
W, H = 1280, 720

# Renkler (dataviz referans paleti, açık yüzey)
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID = "#1b1b1b", "#52514e", "#7a7975", "#e8e7e3"
MARKA = "#0f4c5c"
DON = "Oca–Eki 2026"
AY = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def tr(n, ond=0):
    s = f"{n:,.{ond}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def mn(n, ond=1):
    return tr(n / 1e6, ond) + " Mn ₺"


def e(s):
    return html.escape(str(s))


ORTAK = f"""
*{{box-sizing:border-box}} html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{font-family:"Segoe UI",system-ui,sans-serif;color:{INK};-webkit-font-smoothing:antialiased}}
svg text{{font-family:"Segoe UI",system-ui,sans-serif}}
"""


# ---------- SVG parçaları ----------
def hbar(rows, w, h, renk=S1, fmt=mn, etiket_w=130, cizgi=True):
    """rows: [(etiket, değer)] -> yatay çubuk; 4px yuvarlak uç, değer etiketi metin renginde."""
    n = len(rows); mx = max(v for _, v in rows) or 1
    satir = h / n; bh = min(18, satir * .62); bw = w - etiket_w - 78
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    for i, (ad, v) in enumerate(rows):
        y = i * satir + (satir - bh) / 2; L = max(2, bw * v / mx)
        out.append(f'<text x="{etiket_w - 10}" y="{y + bh / 2 + 4}" text-anchor="end" font-size="12" fill="{INK2}">{e(ad)}</text>')
        out.append(f'<path d="M{etiket_w} {y}h{L - 4}a4 4 0 0 1 4 4v{bh - 8}a4 4 0 0 1-4 4h{-(L - 4)}z" fill="{renk}"/>')
        out.append(f'<text x="{etiket_w + L + 7}" y="{y + bh / 2 + 4}" font-size="11.5" fill="{INK}" font-weight="600">{e(fmt(v))}</text>')
    if cizgi:
        out.append(f'<line x1="{etiket_w}" x2="{etiket_w}" y1="0" y2="{h}" stroke="#cfcdc8" stroke-width="1"/>')
    out.append("</svg>")
    return "".join(out)


def cizgi_grafik(deg, w, h, renk=S1, y_fmt=lambda v: tr(v / 1e6, 0), alan=True, kolon=False):
    pl, pr, pt, pb = 44, 14, 14, 30
    iw, ih = w - pl - pr, h - pt - pb
    mx = max(deg) * 1.12; n = len(deg)
    ham = mx / 4; us = 10 ** (len(str(int(ham))) - 1)
    adim = next(us * k for k in (1, 2, 2.5, 5, 10) if us * k >= ham)
    out = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    t = 0
    while t <= mx:
        y = pt + ih - ih * t / mx
        out.append(f'<line x1="{pl}" x2="{w - pr}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pl - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{y_fmt(t)}</text>')
        t += adim
    xs = [pl + iw * (i + .5) / n for i in range(n)]
    ys = [pt + ih - ih * v / mx for v in deg]
    if kolon:
        bw = iw / n * .62
        for x, y in zip(xs, ys):
            hh = pt + ih - y
            if hh < 4:
                out.append(f'<rect x="{x - bw / 2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{renk}"/>')
            else:
                out.append(f'<path d="M{x - bw / 2:.1f} {pt + ih}V{y + 4:.1f}a4 4 0 0 1 4-4h{bw - 8:.1f}a4 4 0 0 1 4 4V{pt + ih}z" fill="{renk}"/>')
    else:
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, ys))
        if alan:
            out.append(f'<defs><linearGradient id="g{renk[1:]}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{renk}" stop-opacity=".22"/><stop offset="1" stop-color="{renk}" stop-opacity="0"/></linearGradient></defs>')
            out.append(f'<path d="{d} L{xs[-1]:.1f} {pt + ih} L{xs[0]:.1f} {pt + ih}Z" fill="url(#g{renk[1:]})"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{renk}" stroke-width="2" stroke-linejoin="round"/>')
        i = deg.index(max(deg))
        out.append(f'<circle cx="{xs[i]:.1f}" cy="{ys[i]:.1f}" r="4.5" fill="{renk}" stroke="#fff" stroke-width="2"/>')
        out.append(f'<text x="{xs[i]:.1f}" y="{ys[i] - 10:.1f}" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK}">{mn(deg[i])}</text>')
    out.append(f'<line x1="{pl}" x2="{w - pr}" y1="{pt + ih}" y2="{pt + ih}" stroke="#bdbbb5"/>')
    for i, a in enumerate(V["aylar"]):
        yil, ay = a.split("-")
        if ay in ("01", "07"):
            lab = f"{AY[int(ay) - 1]} {yil}" if ay == "01" else AY[int(ay) - 1]
            out.append(f'<text x="{xs[i]:.1f}" y="{h - 10}" text-anchor="middle" font-size="11" fill="{MUTED}">{lab}</text>')
        if ay == "01" and i:
            x = (xs[i] + xs[i - 1]) / 2
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{pt}" y2="{pt + ih}" stroke="#cfcdc8" stroke-dasharray="3 3"/>')
    out.append("</svg>")
    return "".join(out)


def pbi_sayfa(baslik, aktif, govde):
    sekmeler = "".join(f'<span class="{"on" if s == aktif else ""}">{s}</span>' for s in ("Genel Bakış", "İade Analizi", "Müşteriler"))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{ORTAK}
body{{background:#e9e8e4}}
.app{{position:absolute;inset:0;display:flex;flex-direction:column}}
.bar{{height:30px;background:#2b2b2b;color:#ddd;font-size:12px;display:flex;align-items:center;padding:0 12px;gap:18px}}
.bar b{{color:#f2c811;font-weight:700}}
.canvas{{flex:1;margin:10px 14px 0;background:#f6f5f2;border-radius:2px;box-shadow:0 1px 3px rgba(0,0,0,.18);padding:0;display:flex;flex-direction:column;overflow:hidden}}
.hd{{height:54px;background:{MARKA};color:#fff;display:flex;align-items:center;padding:0 18px;gap:14px}}
.logo{{width:32px;height:32px;border-radius:7px;background:#fff;color:{MARKA};font:700 13px/32px "Segoe UI";text-align:center}}
.hd h1{{margin:0;font-size:19px;font-weight:600;letter-spacing:.01em}}
.hd small{{display:block;font-size:11px;opacity:.75;font-weight:400}}
.sl{{margin-left:auto;display:flex;gap:8px}}
.sl span{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:6px;padding:5px 10px;font-size:11.5px}}
.sl span i{{font-style:normal;opacity:.7;margin-right:4px}}
.g{{flex:1;display:grid;gap:10px;padding:10px}}
.k{{background:#fff;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,.06);padding:10px 14px;position:relative;overflow:hidden}}
.k h3{{margin:0 0 6px;font-size:12px;font-weight:600;color:{INK2}}}
.kpi .v{{font-size:24px;font-weight:600;letter-spacing:-.01em}}
.kpi .d{{font-size:11px;color:{MUTED};margin-top:2px}}
.kpi .d b{{color:{INK};font-weight:600}}
.kpi:before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:{MARKA}}}
table{{border-collapse:collapse;width:100%;font-size:12px}}
th{{text-align:left;font-weight:600;color:{INK2};border-bottom:1px solid #d6d4cf;padding:5px 6px}}
td{{padding:5px 6px;border-bottom:1px solid #efeeea}} td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums}}
tr.top td{{font-weight:600;border-top:1px solid #bdbbb5;border-bottom:0}}
.tabs{{height:28px;display:flex;gap:2px;padding:0 14px;align-items:flex-end;background:#e9e8e4}}
.tabs span{{font-size:11.5px;padding:5px 14px;background:#dcdbd6;color:#555;border-radius:4px 4px 0 0}}
.tabs span.on{{background:#fff;color:#111;font-weight:600;border-bottom:2px solid {S4}}}
</style></head><body><div class="app">
<div class="bar"><b>Power BI</b><span>Dosya</span><span>Giriş</span><span>Ekle</span><span>Modelleme</span><span>Görünüm</span><span style="margin-left:auto;opacity:.7">Kırak Metal Satış.pbix</span></div>
<div class="canvas"><div class="hd"><div class="logo">KM</div><div><h1>{baslik}</h1><small>Kırak Metal · Ocak 2024 – Ekim 2026 · {tr(V['satir'])} sipariş satırı · karşılaştırma: Oca–Eki, önceki yıl</small></div>
<div class="sl"><span><i>Yıl</i>Tümü ▾</span><span><i>Bölge</i>Tümü ▾</span><span><i>Kategori</i>Tümü ▾</span></div></div>
{govde}</div><div class="tabs">{sekmeler}</div></div></body></html>"""


def kpi(baslik, deger, alt):
    return f'<div class="k kpi"><h3>{baslik}</h3><div class="v">{deger}</div><div class="d">{alt}</div></div>'


def degisim(a, b):
    p = (a - b) / b * 100
    return f'{"▲" if p >= 0 else "▼"} %{tr(abs(p), 1)}'


def satis_paneli():
    y = V["yil"]; c = sum(d["ciro"] for d in y.values()); k = sum(d["kar"] for d in y.values())
    s = sum(d["siparis"] for d in y.values())
    y6, y5 = V["ytd"]["2026"], V["ytd"]["2025"]
    kp = "".join([
        kpi("Toplam Ciro", mn(c), f'{DON}: <b>{mn(y6["ciro"])}</b> · {degisim(y6["ciro"], y5["ciro"])}'),
        kpi("Brüt Kâr", mn(k), f'{DON}: <b>{mn(y6["kar"])}</b> · {degisim(y6["kar"], y5["kar"])}'),
        kpi("Kâr Marjı", f"%{tr(k / c * 100, 1)}", f'{DON}: <b>%{tr(y6["kar"] / y6["ciro"] * 100, 1)}</b>'),
        kpi("Sipariş", tr(s), f'{DON}: <b>{tr(y6["siparis"])}</b> · {degisim(y6["siparis"], y5["siparis"])}'),
        kpi("Ort. Sevk Süresi", f'{tr(sum(d["sevk"] for d in y.values()) / 3, 1)} gün', f'2026: <b>{tr(V["yil"]["2026"]["sevk"], 2)} gün</b>'),
    ])
    trend = cizgi_grafik(V["ay_ciro"], 690, 200)
    katg = hbar([(a, v) for a, v, *_ in V["kat"]], 450, 196, etiket_w=140)
    bol = hbar([(a, v) for a, v, *_ in V["bolge"]], 690, 196, etiket_w=140)
    rows = "".join(f'<tr><td>{e(a)}</td><td class="n">{mn(v, 2)}</td><td class="n">%{tr(kk / v * 100, 1)}</td></tr>' for a, v, kk in V["urun_top"])
    tablo = f'<table><tr><th>Ürün</th><th class="n">Ciro</th><th class="n">Marj</th></tr>{rows}</table>'
    govde = f"""<div class="g" style="grid-template-columns:repeat(5,1fr);grid-template-rows:84px 238px 1fr">
{kp}
<div class="k" style="grid-column:span 3"><h3>Aylık Ciro (Mn ₺)</h3>{trend}</div>
<div class="k" style="grid-column:span 2"><h3>Kategoriye Göre Ciro</h3>{katg}</div>
<div class="k" style="grid-column:span 3"><h3>Bölgeye Göre Ciro</h3>{bol}</div>
<div class="k" style="grid-column:span 2"><h3>En Çok Ciro Getiren Ürünler</h3>{tablo}</div>
</div>"""
    return pbi_sayfa("Satış Performansı", "Genel Bakış", govde)


def iade_paneli():
    y = V["yil"]; ti = sum(d["iade"] for d in y.values()); ta = sum(d["adet"] for d in y.values())
    y6, y5 = V["ytd"]["2026"], V["ytd"]["2025"]
    kat = sorted(V["kat"], key=lambda r: -r[3])
    kp = "".join([
        kpi("İade Edilen Adet", tr(ti), f'{DON}: <b>{tr(y6["iade"])}</b> · {degisim(y6["iade"], y5["iade"])}'),
        kpi("İade Oranı", f"‰{tr(ti / ta * 1000, 2)}", f'{DON}: <b>‰{tr(y6["iade"] / y6["adet"] * 1000, 2)}</b>'),
        kpi("En Çok İade", e(kat[0][0]), f'<b>{tr(kat[0][3])}</b> adet · tüm iadelerin %{tr(kat[0][3] / ti * 100, 0)}\'i'),
        kpi("İadesiz Bölge", "2 / 9", "Bulgaristan · Doğu Anadolu"),
    ])
    kolon = cizgi_grafik(V["ay_iade"], 880, 206, renk=S2, y_fmt=lambda v: tr(v), kolon=True)
    # Bölge x yıl ısı tablosu (binde iade oranı), tek ton sıralı
    yillar = ["2024", "2025", "2026"]
    oran = {b: [(d[yl][0] / d[yl][1] * 1000 if d[yl][1] else 0) for yl in yillar] for b, d in V["bolge_yil"].items()}
    mx = max(max(v) for v in oran.values()) or 1
    def hucre(v):
        t = v / mx
        a = 0.08 + 0.85 * t
        renk = "#fff" if t > .55 else INK
        return f'<td class="n" style="background:color-mix(in srgb,{S1} {a * 100:.0f}%,#fff);color:{renk}">{tr(v, 2) if v else "–"}</td>'
    sira = sorted(oran, key=lambda b: -sum(oran[b]))
    satir = "".join(f'<tr><td>{e(b)}</td>{"".join(hucre(v) for v in oran[b])}</tr>' for b in sira)
    isi = f'<table class="isi"><tr><th>Bölge</th>{"".join(f"<th class=n>{yl}</th>" for yl in yillar)}</tr>{satir}</table>'
    urun = hbar([(a[:26], v) for a, v in V["urun_iade_top"]], 520, 176, renk=S2, fmt=lambda v: tr(v) + " adet", etiket_w=190)
    govde = f"""<style>.isi td{{padding:3.6px 8px;border-bottom:2px solid #fff}} .isi th{{padding:4px 8px}}</style>
<div class="g" style="grid-template-columns:repeat(4,1fr);grid-template-rows:84px 250px 1fr">
{kp}
<div class="k" style="grid-column:span 3"><h3>Aylık İade Adedi</h3>{kolon}</div>
<div class="k" style="grid-column:span 1;grid-row:span 2"><h3>İade Oranı, Bölge × Yıl (‰)</h3>{isi}
<p style="font-size:11px;color:{MUTED};margin:8px 0 0">Koyu hücre = yüksek iade oranı. Satılan 1.000 adette kaç adet geri döndü.</p></div>
<div class="k" style="grid-column:span 3"><h3>En Çok İade Edilen Ürünler</h3>{urun}</div>
</div>"""
    return pbi_sayfa("İade Analizi", "İade Analizi", govde)


def sql_ekrani():
    kw = lambda s: f'<span class="kw">{s}</span>'
    fn = lambda s: f'<span class="fn">{s}</span>'
    satirlar = [
        f'<span class="cm">-- Kırak Metal: en çok ciro getiren 8 müşteri (2024–2026)</span>',
        f'{kw("USE")} KirakMetal;',
        '',
        f'{kw("SELECT TOP")} 8',
        f'    m.Firma, m.Sehir, b.Bolge,',
        f'    {fn("COUNT")}({kw("DISTINCT")} s.SiparisNo)        {kw("AS")} Siparis,',
        f'    {fn("SUM")}(s.Adet)                        {kw("AS")} ToplamAdet,',
        f'    {fn("SUM")}(s.Adet * u.UrunFiyati)         {kw("AS")} Ciro',
        f'{kw("FROM")} dbo.Satis {kw("AS")} s',
        f'{kw("JOIN")} dbo.Musteri {kw("AS")} m {kw("ON")} m.MusteriKey = s.MusteriKey',
        f'{kw("JOIN")} dbo.Urun    {kw("AS")} u {kw("ON")} u.UrunKey    = s.UrunKey',
        f'{kw("JOIN")} dbo.Bolge   {kw("AS")} b {kw("ON")} b.BolgeKey   = s.BolgeKey',
        f'{kw("GROUP BY")} m.MusteriKey, m.Firma, m.Sehir, b.Bolge',
        f'{kw("ORDER BY")} Ciro {kw("DESC")};',
    ]
    kod = "".join(f'<div><i>{i + 1}</i>{s or "&nbsp;"}</div>' for i, s in enumerate(satirlar))
    sonuc = "".join(
        f'<tr><td class="no">{i + 1}</td><td>{e(f)}</td><td>{e(sh)}</td><td>{e(b)}</td><td class="n">{tr(sp)}</td><td class="n">{tr(ad)}</td><td class="n">{tr(c, 2)}</td></tr>'
        for i, (f, sh, b, sp, ad, c) in enumerate(V["musteri_top"]))
    agac = "".join(f'<div style="padding-left:{p}px">{t}</div>' for p, t in [
        (0, "▾ 🖥 localhost\\SQLEXPRESS"), (14, "▾ 📁 Databases"), (28, "▾ 🗄 KirakMetal"), (42, "▾ 📁 Tables"),
        (56, "▦ dbo.Bolge"), (56, "▦ dbo.Iade"), (56, "▦ dbo.Musteri"), (56, "▦ dbo.Satis"), (56, "▦ dbo.Takvim"), (56, "▦ dbo.Urun"),
        (42, "▸ 📁 Views"), (28, "▸ 🗄 MyDatabase"), (28, "▸ 🗄 SalesDB")])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{ORTAK}
body{{background:#eef0f4;font-size:13px}}
.top{{height:30px;background:#2d3a52;color:#e7ebf3;display:flex;align-items:center;gap:16px;padding:0 12px;font-size:12px}}
.top b{{font-weight:600}}
.tool{{height:34px;background:#f5f6f9;border-bottom:1px solid #d5d9e2;display:flex;align-items:center;gap:10px;padding:0 10px;font-size:12px}}
.tool .run{{background:#fff;border:1px solid #c9cfda;border-radius:3px;padding:3px 10px;color:#1e7e34;font-weight:600}}
.tool .db{{background:#fff;border:1px solid #c9cfda;padding:3px 10px;border-radius:3px}}
.main{{display:flex;height:{H - 64}px}}
.oe{{width:230px;background:#fff;border-right:1px solid #d5d9e2;font-size:12px;line-height:22px;padding:6px 8px;color:#222}}
.oe h4{{margin:0 0 4px;font-size:11.5px;color:#555;font-weight:600;border-bottom:1px solid #e3e6ec;padding-bottom:4px}}
.ed{{flex:1;display:flex;flex-direction:column;min-width:0}}
.tab{{height:28px;background:#e6e9ef;display:flex;align-items:flex-end;padding-left:6px}}
.tab span{{background:#fff;padding:5px 14px;font-size:12px;border-top:2px solid #f0a30a}}
.code{{background:#fff;font:13px/20.5px Consolas,"Cascadia Mono",monospace;padding:8px 0;height:316px;color:#000}}
.code div{{white-space:pre}} .code i{{display:inline-block;width:38px;text-align:right;color:#2b91af;font-style:normal;margin-right:14px}}
.kw{{color:#0000ff}} .fn{{color:#ff00ff}} .cm{{color:#008000}}
.res{{flex:1;background:#fff;border-top:4px solid #e6e9ef;display:flex;flex-direction:column}}
.rt{{font-size:12px;padding:4px 10px;background:#f5f6f9;border-bottom:1px solid #dde1e8}} .rt b{{font-weight:600;border-bottom:2px solid #2d3a52;padding-bottom:2px}}
table{{border-collapse:collapse;font-size:12.5px;margin:0;width:100%}}
th{{background:#f3f4f7;border:1px solid #d7dbe3;font-weight:400;padding:3px 8px;text-align:left}}
td{{border:1px solid #e6e9ef;padding:3px 8px;white-space:nowrap}} td.n{{text-align:right;font-variant-numeric:tabular-nums}}
td.no{{background:#f3f4f7;color:#555;text-align:center;width:30px}}
tr:first-child+tr td:not(.no){{outline:1px dotted #333;outline-offset:-2px}}
.st{{height:24px;background:#f0a30a;color:#1b1b1b;font-size:12px;display:flex;align-items:center;gap:22px;padding:0 10px;margin-top:auto}}
</style></head><body>
<div class="top"><b>SQL Server Management Studio</b><span>Dosya</span><span>Düzen</span><span>Görünüm</span><span>Sorgu</span><span>Araçlar</span></div>
<div class="tool"><span class="db">KirakMetal ▾</span><span class="run">▶ Execute</span><span style="color:#666">✓ Parse</span></div>
<div class="main"><div class="oe"><h4>Object Explorer</h4>{agac}</div>
<div class="ed"><div class="tab"><span>Musteri Analizi.sql — localhost\\SQLEXPRESS</span></div>
<div class="code">{kod}</div>
<div class="res"><div class="rt"><b>▦ Results</b> &nbsp; Messages</div>
<table><tr><th></th><th>Firma</th><th>Sehir</th><th>Bolge</th><th>Siparis</th><th>ToplamAdet</th><th>Ciro</th></tr>{sonuc}</table>
<div class="st"><span>✓ Query executed successfully.</span><span style="margin-left:auto">localhost\\SQLEXPRESS</span><span>KirakMetal</span><span>00:00:00</span><span>8 rows</span></div></div>
</div></div></body></html>"""


def excel_ekrani():
    onceki = [V["ay_ciro"][i] for i, a in enumerate(V["aylar"]) if a.startswith("2025")]
    gercek = [V["ay_ciro"][i] for i, a in enumerate(V["aylar"]) if a.startswith("2026")]
    buyume = 0.08
    butce = [c * (1 + buyume) for c in onceki]
    aylik, n_g = butce, len(gercek)
    mx = max(max(butce), max(gercek))
    sutun = list("ABCDEFGH")
    gen = [34, 70, 116, 116, 116, 84, 160, 40]
    def bas():
        return '<tr class="h"><td class="rh"></td>' + "".join(f'<td style="width:{g}px">{c}</td>' for c, g in zip(sutun, gen)) + "</tr>"
    def satir(n, hucreler, cls=""):
        h = "".join(f"<td{(' ' + a) if a else ''}>{v}</td>" for v, a in hucreler)
        import re as _re
        dolu = sum(int(m.group(1)) if (m := _re.search(r'colspan="(\d+)"', a)) else 1 for _, a in hucreler)
        bos = len(sutun) - dolu
        return f'<tr class="{cls}"><td class="rh">{n}</td>{h}{"<td></td>" * bos}</tr>'
    rows = [bas(),
            satir(1, [("", ""), ('<b style="font-size:15px">Kırak Metal · 2026 Bütçe ve Gerçekleşen</b>', 'colspan="6"')]),
            satir(2, [("", ""), ("Senaryo", 'class="lb"'), ("Baz ▾", 'class="in"'), ("", ""), ("Bütçe = 2025 gerçek × (1 + büyüme)", 'class="mt" colspan="3"')]),
            satir(3, [("", ""), ("Satış büyümesi", 'class="lb"'), ("%8,0", 'class="in n"'), ("", ""), ("Sarı hücreler girdi, gerisi formül.", 'class="mt" colspan="3"')]),
            satir(4, [("", ""), ("Son veri", 'class="lb"'), ("Ekim 2026", 'class="n"')]),
            satir(5, []),
            satir(6, [("", ""), ("Ay", 'class="th"'), ("2025 Gerçek", 'class="th n"'), ("2026 Bütçe", 'class="th n"'), ("2026 Gerçek", 'class="th n"'), ("Sapma", 'class="th n"'), ("Gerçek / Bütçe", 'class="th"')])]
    for i in range(12):
        sec = ' sel' if i == 3 else ''
        if i < n_g:
            s = (gercek[i] - butce[i]) / butce[i] * 100
            renk = "#1a7f37" if s >= 0 else "#c4321b"
            sap = (f'<span style="color:{renk};font-weight:600">{"▲" if s >= 0 else "▼"} %{tr(abs(s), 1)}</span>', f'class="n{sec}"')
            w = min(gercek[i] / butce[i], 1.25) / 1.25 * 100
            bar = (f'<div class="db{" eks" if s < 0 else ""}" style="width:{w:.0f}%"></div><div class="hedef"></div>', 'class="dbc"')
            g = (tr(gercek[i]), 'class="n"')
        else:
            g, sap, bar = ("–", 'class="n mt2"'), ("", ""), ("", "")
        rows.append(satir(7 + i, [("", ""), (AY[i], 'class="lb2"'), (tr(onceki[i]), 'class="n"'), (tr(butce[i]), 'class="n"'), g, sap, bar]))
    tb = sum(butce[:n_g]); tg = sum(gercek)
    ts = (tg - tb) / tb * 100
    rows.append(satir(19, [("", ""), ("Oca–Eki", 'class="tt"'), (tr(sum(onceki[:n_g])), 'class="n tt"'), (tr(tb), 'class="n tt"'),
                           (tr(tg), 'class="n tt"'), (f'{"▲" if ts >= 0 else "▼"} %{tr(abs(ts), 1)}', 'class="n tt"'), ("", 'class="tt"')]))
    rows.append(satir(20, [("", ""), ("Yıl", 'class="lb2"'), (tr(sum(onceki)), 'class="n"'), (tr(sum(butce)), 'class="n"'), ("", ""), ("", "")]))
    for n in range(21, 24):
        rows.append(satir(n, []))
    sekme = "".join(f'<span class="{"on" if s == "Bütçe" else ""}">{s}</span>' for s in ("Özet", "Varsayımlar", "Bütçe", "2026 Veri"))
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{ORTAK}
body{{background:#fff;font-size:12.5px}}
.tb{{height:32px;background:#107c41;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12.5px;position:relative}}
.tb b{{position:absolute;left:12px;font-weight:600}}
.rb{{height:30px;background:#f3f3f3;border-bottom:1px solid #dadada;display:flex;gap:20px;align-items:center;padding:0 14px;font-size:12.5px;color:#333}}
.rb .on{{color:#107c41;font-weight:600;border-bottom:2px solid #107c41;padding-bottom:4px}}
.rib{{height:58px;background:#fbfbfb;border-bottom:1px solid #dadada;display:flex;gap:26px;align-items:center;padding:0 16px;color:#444;font-size:11.5px}}
.rib div{{display:flex;flex-direction:column;align-items:center;gap:3px}} .rib i{{font-style:normal;font-size:17px}}
.fx{{height:28px;border-bottom:1px solid #dadada;display:flex;align-items:center;font:12.5px Consolas,monospace}}
.fx .nm{{width:92px;border-right:1px solid #dadada;padding:0 8px;font-family:"Segoe UI"}} .fx .f{{padding:0 10px;color:#777}} .fx .v{{color:#111}}
.wrap{{display:flex}}
table{{border-collapse:collapse;table-layout:fixed}}
td{{border:1px solid #e1e1e1;height:22px;padding:0 6px;white-space:nowrap;overflow:hidden}}
tr.h td{{background:#f3f3f3;color:#555;text-align:center;font-size:11.5px;height:20px}}
td.rh{{background:#f3f3f3;color:#555;text-align:center;width:34px;font-size:11.5px}}
td.n{{text-align:right;font-variant-numeric:tabular-nums}}
td.lb{{color:#333}} td.lb2{{color:#333;font-weight:600}} td.mt{{color:#888;font-style:italic;border-color:transparent}}
td.in{{background:#fff4c2;color:#7a5a00;font-weight:600;border:1px solid #e3c14a}}
td.th{{background:#0f4c5c;color:#fff;font-weight:600}}
td.tt{{font-weight:700;border-top:2px solid #333;background:#f4f8f6}}
td.sel{{outline:2px solid #107c41;outline-offset:-2px;background:#e8f2ec}}
td.dbc{{padding:3px 6px}} .dbc{{position:relative}} .hedef{{position:absolute;top:2px;bottom:2px;left:calc(6px + (100% - 12px) * .8);width:2px;background:#333}} .db.eks{{background:linear-gradient(90deg,{S2},color-mix(in srgb,{S2} 35%,#fff))}} td.mt2{{color:#aaa}}
.db{{height:14px;background:linear-gradient(90deg,{S1},color-mix(in srgb,{S1} 35%,#fff));border-radius:0 3px 3px 0}}
.ch{{margin:44px 0 0 26px;width:330px;height:250px;border:1px solid #d9d9d9;background:#fff;padding:10px 12px;box-shadow:0 2px 6px rgba(0,0,0,.08)}}
.ch h4{{margin:0 0 6px;font-size:13px;font-weight:600;color:#333}}
.sh{{position:absolute;bottom:0;left:0;right:0;height:30px;background:#f3f3f3;border-top:1px solid #dadada;display:flex;gap:2px;padding-left:44px;align-items:flex-start}}
.sh span{{padding:5px 16px;font-size:12px;color:#444}} .sh span.on{{background:#fff;color:#107c41;font-weight:600;border-bottom:2px solid #107c41}}
</style></head><body>
<div class="tb"><b>Excel</b>Kırak Metal Bütçe 2026.xlsx</div>
<div class="rb"><span>Dosya</span><span class="on">Giriş</span><span>Ekle</span><span>Sayfa Düzeni</span><span>Formüller</span><span>Veri</span><span>Gözden Geçir</span><span>Görünüm</span></div>
<div class="rib"><div><i>📋</i>Yapıştır</div><div><i>𝐁</i>Kalın</div><div><i>%</i>Yüzde</div><div><i>▤</i>Koşullu Biçim.</div><div><i>▦</i>Tablo Olarak</div><div><i>Σ</i>Otomatik Toplam</div><div><i>⇅</i>Sırala</div></div>
<div class="fx"><span class="nm">F10</span><span class="f">fx</span><span class="v">=EĞERHATA(E10/D10-1;"")</span></div>
<div class="wrap"><table>{"".join(rows)}</table>
<div class="ch"><h4>2026 Bütçe ve Gerçek (Mn ₺)</h4>{cizgi_ikili(butce, gercek)}</div></div>
<div class="sh">{sekme}</div>
</body></html>"""


def cizgi_ikili(a, b):
    w, h = 306, 200; pl, pb, pt = 30, 34, 8; iw, ih = w - pl - 6, h - pb - pt
    mx = max(max(a), max(b)) * 1.1
    out = [f'<svg width="{w}" height="{h}">']
    for t in range(0, int(mx / 1e6) + 1, 3):
        y = pt + ih - ih * t * 1e6 / mx
        out.append(f'<line x1="{pl}" x2="{w}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/><text x="{pl - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="10" fill="{MUTED}">{t}</text>')
    for seri, renk in ((a, "#9b9a95"), (b, S1)):
        pts = " ".join(f"{pl + iw * (i + .5) / 12:.1f},{pt + ih - ih * v / mx:.1f}" for i, v in enumerate(seri))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{renk}" stroke-width="2"/>')
    for i in range(0, 12, 2):
        out.append(f'<text x="{pl + iw * (i + .5) / 12:.1f}" y="{pt + ih + 15}" text-anchor="middle" font-size="10" fill="{MUTED}">{AY[i]}</text>')
    out.append(f'<rect x="{pl}" y="{h - 12}" width="14" height="3" fill="#9b9a95"/><text x="{pl + 19}" y="{h - 7}" font-size="10.5" fill="{INK2}">2026 Bütçe</text>')
    out.append(f'<rect x="{pl + 110}" y="{h - 12}" width="14" height="3" fill="{S1}"/><text x="{pl + 129}" y="{h - 7}" font-size="10.5" fill="{INK2}">2026 Gerçek</text>')
    out.append("</svg>")
    return "".join(out)


def cek(ad, icerik):
    h = KOK / "out" / f"{ad}.html"; h.parent.mkdir(exist_ok=True)
    h.write_text(icerik, encoding="utf-8")
    png = CIKTI / f"{ad}.png"
    subprocess.run([BRAVE, "--headless", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=3000",
                    "--force-device-scale-factor=1.5", f"--window-size={W},{H}", f"--screenshot={png}", h.as_uri()],
                   capture_output=True, timeout=90)
    print(ad, png.exists())


if __name__ == "__main__":
    cek("pbi-satis", satis_paneli())
    cek("pbi-iade", iade_paneli())
    cek("sql-musteri", sql_ekrani())
    cek("excel-butce", excel_ekrani())
