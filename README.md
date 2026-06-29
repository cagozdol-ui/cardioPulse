# CardioPulse — Kardiyoloji Makale Radarı

PubMed'den genel kardiyoloji ve girişimsel/koroner kardiyoloji dergilerinde
yayınlanan makaleleri her gün otomatik çekip dergi kalitesi, makale tipi ve
güncellik baz alınarak skorlayan, ücretsiz ve açık bir araç.

## Nasıl çalışıyor

1. `fetch_and_score.py` — PubMed E-utilities üzerinden son 7 günün makalelerini
   çeker, skorlar, `data/latest.json` dosyasına yazar.
2. `generate_html.py` — bu JSON'dan iki sekmeli (`Genel Kardiyoloji` /
   `Girişimsel & Koroner`) statik bir sayfa üretir: `docs/index.html`.
3. `.github/workflows/daily-update.yml` — bu iki script'i her gün 08:00 TRT'de
   otomatik çalıştırır ve sonucu repo'ya commit'ler.

Dergi listeleri ve skorlama ağırlıkları `config.py` içinde — istediğin gibi
dergi ekleyip çıkarabilir, ağırlıkları değiştirebilirsin.

## Kurulum (10 dakika)

1. **GitHub'da yeni bir repo aç** (public — ücretsiz Pages için gerekli),
   örn. `cardiopulse`. Bu klasördeki tüm dosyaları o repo'ya yükle (push et).

2. **(Önerilir) Ücretsiz NCBI API key al:**
   https://www.ncbi.nlm.nih.gov/account/settings/ → "API Key Management".
   Bu, istek limitini 3/sn'den 10/sn'ye çıkarır, çekim daha hızlı olur.

3. **API key'i GitHub'a secret olarak ekle:**
   Repo → Settings → Secrets and variables → Actions → "New repository secret"
   → İsim: `NCBI_API_KEY`, değer: aldığın key.
   (Bu adımı atlarsan script API key'siz de çalışır, sadece biraz daha yavaş çeker.)

4. **GitHub Pages'i aç:**
   Repo → Settings → Pages → "Source" kısmından `Deploy from a branch` seç,
   branch: `main`, klasör: `/docs`. Kaydet.

5. **Workflow'u ilk kez manuel çalıştır:**
   Repo → Actions sekmesi → "CardioPulse Günlük Güncelleme" → "Run workflow".
   Birkaç dakika içinde `docs/index.html` güncellenip commit'lenecek.

6. Sayfan şu adreste yayında olacak (kullanıcı adın ve repo adına göre):
   `https://<kullanici-adin>.github.io/cardiopulse/`

Bundan sonra her gün otomatik, sunucu yönetimi veya maliyet olmadan
güncellenir.

## Yerelde test etmek istersen

```bash
pip install -r requirements.txt
python fetch_and_score.py   # gerçek PubMed verisiyle data/latest.json üretir
python generate_html.py     # docs/index.html üretir, tarayıcıda aç
```

## Dergi listelerini özelleştirme

`config.py` içindeki `GENERAL_TIER1`, `GENERAL_TIER2`,
`INTERVENTIONAL_TIER1`, `INTERVENTIONAL_TIER2` listelerine PubMed'in
**TA (dergi başlığı) alanına uyan tam isimle** dergi ekle. Doğru ismi bulmak
için PubMed'de dergiyi ara, bir makalenin künyesinde geçen tam başlığı kullan.

## Not

`data/latest.json` içindeki örnek/demo veriler `[ÖRNEK]` etiketiyle
işaretlenmiştir ve gerçek değildir — sadece tasarımı önizlemek içindir.
İlk gerçek çalıştırmada bu dosyanın üzerine yazılır.
