"""Kırak Metal verisinden proje görselleri için özet rakamlar (veri.json).
Kaynak: Masaüstü/Claude Çıktıları/Power BI Çalışma/04_Kaynak (repo dışında)."""
import csv, json
from collections import defaultdict
from datetime import date
from pathlib import Path

K = Path.home() / "Desktop" / "Claude Çıktıları" / "Power BI Çalışma" / "04_Kaynak"
H = K / "Hazir Tablolar"


def oku(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def sayi(s):
    return float(s.replace(".", "").replace(",", ".")) if s else 0.0


def tarih(s):
    g, a, y = s.split(".")
    return date(int(y), int(a), int(g))


urun = {r["UrunKey"]: r for r in oku(H / "Urun Lookup.csv")}
alt = {r["AltKategoriKey"]: r for r in oku(H / "Urun Alt Kategori Lookup.csv")}
kat = {r["KategoriKey"]: r["KategoriAdi"] for r in oku(H / "Urun Kategori Lookup.csv")}
bolge = {r["BolgeKey"]: r for r in oku(H / "Bolge Lookup.csv")}
musteri = {r["MusteriKey"]: r for r in oku(H / "Musteri Lookup.csv")}
satis = oku(H / "Satis Verisi.csv")
iade = oku(K / "Iade Verisi.csv")

ay_ciro = defaultdict(float); ay_kar = defaultdict(float); ay_adet = defaultdict(float)
yil = defaultdict(lambda: defaultdict(float))
kat_ciro = defaultdict(float); kat_adet = defaultdict(float)
bol_ciro = defaultdict(float); bol_adet = defaultdict(float)
urun_ciro = defaultdict(float); urun_kar = defaultdict(float)
mus = defaultdict(lambda: {"ciro": 0.0, "siparis": set(), "adet": 0.0})
siparis_yil = defaultdict(set)
sevk = defaultdict(list)
for r in satis:
    t = tarih(r["SiparisTarihi"]); u = urun[r["UrunKey"]]; a = sayi(r["Adet"])
    c = a * sayi(u["UrunFiyati"]); m = a * sayi(u["UrunMaliyeti"])
    ak = f"{t.year}-{t.month:02d}"
    ay_ciro[ak] += c; ay_kar[ak] += c - m; ay_adet[ak] += a
    y = yil[t.year]; y["ciro"] += c; y["kar"] += c - m; y["adet"] += a
    siparis_yil[t.year].add(r["SiparisNo"])
    k = kat[alt[u["AltKategoriKey"]]["KategoriKey"]]
    kat_ciro[k] += c; kat_adet[k] += a
    b = bolge[r["BolgeKey"]]["Bolge"]; bol_ciro[b] += c; bol_adet[b] += a
    urun_ciro[u["UrunAdi"]] += c; urun_kar[u["UrunAdi"]] += c - m
    mm = mus[r["MusteriKey"]]; mm["ciro"] += c; mm["siparis"].add(r["SiparisNo"]); mm["adet"] += a
    if r["SevkTarihi"]:
        sevk[t.year].append((tarih(r["SevkTarihi"]) - t).days)

ay_iade = defaultdict(float); bol_iade = defaultdict(float); kat_iade = defaultdict(float)
bol_yil_iade = defaultdict(float); bol_yil_adet = defaultdict(float)
urun_iade = defaultdict(float)
for r in iade:
    t = tarih(r["IadeTarihi"]); a = sayi(r["IadeAdet"]); u = urun[r["UrunKey"]]
    ay_iade[f"{t.year}-{t.month:02d}"] += a
    b = bolge[r["BolgeKey"]]["Bolge"]; bol_iade[b] += a
    kat_iade[kat[alt[u["AltKategoriKey"]]["KategoriKey"]]] += a
    bol_yil_iade[(b, t.year)] += a
    urun_iade[u["UrunAdi"]] += a
for r in satis:
    t = tarih(r["SiparisTarihi"])
    bol_yil_adet[(bolge[r["BolgeKey"]]["Bolge"], t.year)] += sayi(r["Adet"])
for y in yil:
    yil[y]["iade"] = sum(v for k, v in ay_iade.items() if k.startswith(str(y)))
    yil[y]["siparis"] = len(siparis_yil[y])
    yil[y]["sevk"] = sum(sevk[y]) / len(sevk[y]) if sevk[y] else 0

aylar = sorted(ay_ciro)
son_ay = int(aylar[-1][5:])
ytd = defaultdict(lambda: defaultdict(float)); ytd_sip = defaultdict(set)
for r in satis:
    t = tarih(r["SiparisTarihi"])
    if t.month > son_ay:
        continue
    u = urun[r["UrunKey"]]; a = sayi(r["Adet"]); c = a * sayi(u["UrunFiyati"])
    d = ytd[t.year]; d["ciro"] += c; d["kar"] += c - a * sayi(u["UrunMaliyeti"]); d["adet"] += a
    ytd_sip[t.year].add(r["SiparisNo"])
for k, v in ay_iade.items():
    if int(k[5:]) <= son_ay:
        ytd[int(k[:4])]["iade"] += v
for y in ytd:
    ytd[y]["siparis"] = len(ytd_sip[y])
top_mus = sorted(mus.items(), key=lambda kv: -kv[1]["ciro"])[:8]
out = {
    "aylar": aylar,
    "ay_ciro": [round(ay_ciro[a]) for a in aylar],
    "ay_kar": [round(ay_kar[a]) for a in aylar],
    "ay_adet": [round(ay_adet[a]) for a in aylar],
    "ay_iade": [round(ay_iade.get(a, 0)) for a in aylar],
    "yil": {y: {k: round(v, 2) for k, v in d.items()} for y, d in sorted(yil.items())},
    "ytd": {y: {k: round(v, 2) for k, v in d.items()} for y, d in sorted(ytd.items())},
    "son_ay": son_ay,
    "kat": sorted([[k, round(v), round(kat_adet[k]), round(kat_iade.get(k, 0))] for k, v in kat_ciro.items()], key=lambda x: -x[1]),
    "bolge": sorted([[k, round(v), round(bol_adet[k]), round(bol_iade.get(k, 0))] for k, v in bol_ciro.items()], key=lambda x: -x[1]),
    "bolge_yil": {b: {str(y): [round(bol_yil_iade.get((b, y), 0)), round(bol_yil_adet.get((b, y), 0))] for y in sorted(yil)} for b in bol_ciro},
    "urun_top": sorted([[k, round(v), round(urun_kar[k])] for k, v in urun_ciro.items()], key=lambda x: -x[1])[:6],
    "urun_iade_top": sorted([[k, round(v)] for k, v in urun_iade.items()], key=lambda x: -x[1])[:5],
    "musteri_top": [[m["Firma"], m["Sehir"], bolge[m["BolgeKey"]]["Bolge"], len(d["siparis"]), round(d["adet"]), round(d["ciro"])]
                    for k, d in top_mus for m in [musteri[k]]],
    "satir": len(satis),
}
Path(__file__).with_name("veri.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({k: out[k] for k in ("yil", "kat", "bolge", "satir")}, ensure_ascii=False, indent=1))
