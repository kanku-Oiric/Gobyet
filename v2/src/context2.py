"""Pemilih karakter Gobyet berdasarkan topik (bagian 59-60). Hanya pustaka standar, supaya bisa dibawa ke engine
Battle Royale tanpa dependensi.

    select("Apakah AI bisa punya kesadaran?")
    -> {"primary": "philosopher", "secondary": "technology", "accessory": "laptop", ...}

Aturan:
- Skor domain = jumlah kata kunci yang cocok (batas kata, tanpa beda huruf besar/kecil).
- Primary = domain dengan skor tertinggi. Secondary = domain kedua bila skornya > 0 dan karakternya berbeda.
  Maksimum satu primary + satu secondary (aksesori kecil), tidak pernah tiga kostum.
- Tanpa kecocokan: normal-gblk (karakter default).
- Teologi: hanya kata yang jelas merujuk tradisi tertentu yang memilih Pak Haji atau Priest. Kata umum (agama, Tuhan,
  teologi) mengarah ke Philosopher supaya tidak ada tradisi yang diistimewakan (aturan 7.2). Aksesori sekunder untuk
  kedua tradisi sama jenisnya (buku polos).
- Peran turnamen (wasit, juri, skeptic, champion, defeated) ditetapkan oleh fase turnamen, bukan oleh topik.
"""
import json
import re

DEFAULT = "normal-gblk"

# domain -> (karakter, ikon aksesori, kata kunci)
DOMAINS = {
    "philosophy": ("philosopher", "scroll", [
        "filsafat", "filosofi", "filosofis", "filsuf", "philosophy", "philosophical", "philosopher", "etika", "etis", "ethics",
        "ethical", "moral", "moralitas", "morality", "metafisika", "metaphysics", "epistemologi", "epistemology", "ontologi",
        "ontology", "logika", "logic", "eksistensi", "eksistensial", "existential", "kesadaran", "consciousness", "kehendak bebas",
        "free will", "makna hidup", "meaning of life", "estetika", "aesthetics", "stoik", "stoic", "stoikisme", "nihilisme",
        "utilitarian", "utilitarianisme", "deontologi", "kebajikan", "virtue", "agama", "religion", "tuhan", "god", "teologi",
        "theology", "jiwa", "soul", "pikiran", "mind"]),
    "academic": ("academic", "book", [
        "pendidikan", "education", "sekolah", "school", "universitas", "university", "kampus", "campus", "kuliah", "mahasiswa",
        "student", "kurikulum", "curriculum", "akademik", "akademis", "academic", "gelar", "degree", "dosen", "guru", "teacher",
        "ujian", "exam", "skripsi", "tesis", "thesis", "beasiswa", "scholarship", "literasi", "literacy"]),
    "science": ("scientist", "flask", [
        "sains", "science", "ilmiah", "scientific", "ilmuwan", "scientist", "fisika", "physics", "kimia", "chemistry", "biologi",
        "biology", "eksperimen", "experiment", "evolusi", "evolution", "iklim", "climate", "vaksin", "vaccine", "medis", "medical",
        "kedokteran", "medicine", "astronomi", "astronomy", "kuantum", "quantum", "genetika", "genetics", "laboratorium",
        "laboratory", "virus", "pandemi", "pandemic", "nutrisi", "nutrition", "alam semesta", "universe"]),
    "math": ("mathematician", "formula", [
        "matematika", "mathematics", "math", "maths", "aljabar", "algebra", "kalkulus", "calculus", "geometri", "geometry",
        "statistik", "statistika", "statistics", "probabilitas", "peluang", "probability", "teorema", "theorem", "persamaan",
        "equation", "bilangan prima", "prime number", "aritmetika", "arithmetic", "matematis", "mathematical", "tak hingga",
        "infinity", "pembuktian", "proof"]),
    "technology": ("hacker", "laptop", [
        "teknologi", "technology", "tech", "ai", "kecerdasan buatan", "artificial intelligence", "komputer", "computer",
        "software", "perangkat lunak", "programming", "pemrograman", "coding", "kode", "code", "internet", "digital",
        "algoritma", "algorithm", "siber", "cyber", "keamanan siber", "cybersecurity", "robot", "robotika", "otomasi",
        "automation", "blockchain", "kripto", "crypto", "aplikasi", "app", "llm", "machine learning", "pembelajaran mesin",
        "chatbot", "data", "server", "open source", "hacker", "peretas", "gawai", "gadget", "smartphone", "media digital"]),
    "law": ("lawyer", "lawbook", [
        "hukum", "law", "legal", "undang-undang", "konstitusi", "constitution", "konstitusional", "pengadilan", "court",
        "hak asasi", "human rights", "regulasi", "regulation", "kontrak", "contract", "pidana", "criminal law", "perdata",
        "legislasi", "legislation", "jaksa", "prosecutor", "pengacara", "lawyer", "advokat", "yurisprudensi", "hak cipta",
        "copyright", "paten", "patent", "peraturan", "mahkamah"]),
    "history": ("historian", "oldscroll", [
        "sejarah", "history", "historis", "historical", "sejarawan", "historian", "perang dunia", "world war", "kolonial",
        "kolonialisme", "colonial", "colonialism", "kekaisaran", "empire", "revolusi", "revolution", "kuno", "ancient",
        "arkeologi", "archaeology", "majapahit", "sriwijaya", "romawi", "roman", "yunani kuno", "abad ke", "century",
        "dinasti", "dynasty", "kemerdekaan", "independence", "orde baru", "reformasi"]),
    "economics": ("economist", "calculator", [
        "ekonomi", "economy", "economics", "ekonom", "economist", "keuangan", "finance", "finansial", "financial", "pasar",
        "market", "inflasi", "inflation", "pajak", "tax", "upah", "wage", "harga", "price", "investasi", "investment", "saham",
        "stock", "bisnis", "business", "perdagangan", "trade", "bank", "perbankan", "banking", "moneter", "monetary", "fiskal",
        "fiscal", "kapitalisme", "capitalism", "sosialisme", "socialism", "pdb", "gdp", "utang", "debt", "subsidi", "subsidy",
        "pengangguran", "unemployment", "ubi", "universal basic income", "pendapatan", "income", "kemiskinan", "poverty"]),
    "psychology": ("psychologist", "notebook", [
        "psikologi", "psychology", "psikolog", "psychologist", "kesehatan mental", "mental health", "mental", "kognitif",
        "cognitive", "emosi", "emotion", "perilaku", "behavior", "behaviour", "kepribadian", "personality", "motivasi",
        "motivation", "kebahagiaan", "happiness", "trauma", "depresi", "depression", "kecemasan", "anxiety", "otak", "brain",
        "bias kognitif", "cognitive bias", "kebiasaan", "habit", "stres", "stress", "kecanduan", "addiction"]),
    "sociology": ("sociologist", "network", [
        "sosiologi", "sociology", "sosiolog", "sociologist", "masyarakat", "society", "sosial", "social", "budaya", "culture",
        "kebudayaan", "komunitas", "community", "ketimpangan", "inequality", "kelas sosial", "social class", "gender",
        "urbanisasi", "urbanization", "migrasi", "migration", "media sosial", "social media", "keluarga", "family", "demografi",
        "demography", "populasi", "population", "generasi", "generation", "tradisi", "tradition", "politik identitas"]),
    "engineering": ("engineer", "wrench", [
        "teknik sipil", "rekayasa", "engineering", "insinyur", "engineer", "konstruksi", "construction", "infrastruktur",
        "infrastructure", "jembatan", "bridge", "mesin", "machine", "energi", "energy", "listrik", "electricity", "manufaktur",
        "manufacturing", "arsitektur", "architecture", "transportasi", "transportation", "nuklir", "nuclear", "pembangkit",
        "power plant", "baterai", "battery", "kendaraan listrik", "electric vehicle"]),
    "islam": ("pak-haji", "book", [
        "islam", "islami", "islamic", "muslim", "quran", "al-quran", "alquran", "qur'an", "hadis", "hadith", "fikih", "fiqih",
        "fiqh", "syariah", "sharia", "syariat", "tauhid", "sunnah", "ulama", "masjid", "mosque", "salat", "shalat", "ramadan",
        "ramadhan", "haji", "hajj", "zakat", "akidah", "aqidah", "tafsir", "halal", "haram", "fatwa", "pesantren", "ustaz",
        "ustadz", "kiai"]),
    "christianity": ("priest", "book", [
        "kristen", "kristiani", "christian", "christianity", "katolik", "catholic", "protestan", "protestant", "alkitab", "bible",
        "biblical", "injil", "gospel", "gereja", "church", "yesus", "jesus", "kristus", "christ", "trinitas", "trinity",
        "pendeta", "pastor", "pastur", "sakramen", "sacrament", "misa", "paus", "pope", "vatikan", "vatican", "teologi kristen",
        "christian theology", "kebangkitan kristus", "resurrection"]),
    "investigation": ("detective", "magnifier", [
        "investigasi", "investigation", "penyelidikan", "detektif", "detective", "misteri", "mystery", "forensik", "forensic",
        "kejahatan", "crime", "kriminal", "konspirasi", "conspiracy", "korupsi", "corruption", "skandal", "scandal", "penipuan",
        "fraud", "pelaku", "suspect", "tersangka", "kasus pembunuhan", "murder case"]),
    "knight": ("fantasy-knight", "sword", [
        "ksatria", "knight", "abad pertengahan", "medieval", "kastil", "castle", "feodal", "feodalisme", "feudal", "feudalism",
        "chivalry", "perang salib", "crusade", "turnamen ksatria"]),
    "viking": ("fantasy-viking", "axe", [
        "viking", "vikings", "norse", "nordik", "nordic", "skandinavia", "scandinavia", "odin", "valhalla", "mitologi nordik"]),
    "pirate": ("fantasy-pirate", "telescope", [
        "bajak laut", "pirate", "pirates", "perompak", "maritim", "maritime", "pelayaran", "sailing", "harta karun", "treasure",
        "kapal layar", "sailing ship", "angkatan laut", "navy", "samudra", "ocean"]),
    "magic": ("wizard", "star", [
        "sihir", "magic", "penyihir", "wizard", "fantasi", "fantasy", "mitologi", "mythology", "dongeng", "fairy tale", "mitos",
        "myth", "takhayul", "superstition", "supernatural", "alkimia", "alchemy", "ramalan", "prophecy", "astrologi", "astrology"]),
    "evidence": ("researcher", "papers", [
        "riset", "research", "penelitian", "peneliti", "researcher", "bukti", "evidence", "empiris", "empirical", "studi",
        "study", "meta-analisis", "meta-analysis", "jurnal", "journal", "survei", "survey", "sitasi", "citation", "data empiris"]),
    "falsification": ("skeptic", "question", [
        "skeptis", "skeptisisme", "skeptic", "skepticism", "falsifikasi", "falsification", "pseudosains", "pseudoscience", "hoaks",
        "hoax", "misinformasi", "misinformation", "disinformasi", "disinformation", "teori konspirasi", "conspiracy theory",
        "cek fakta", "fact check", "mitos kesehatan"]),
    "sport": ("referee", "flag", [
        "olahraga", "sport", "sports", "sepak bola", "football", "soccer", "wasit", "referee", "pertandingan", "match",
        "kompetisi", "competition", "liga", "league", "atlet", "athlete", "esports", "e-sport", "piala dunia", "world cup"]),
}

# peran turnamen -> karakter (dipakai engine sesuai fase, bukan dari topik)
ROLES = {"falsification": "skeptic", "evidence": "researcher", "judging": "judge", "tournament": "referee",
         "winner": "champion", "loser": "defeated", "generic": DEFAULT}

# ikon aksesori 16x16: nama -> (item, kw, grip di kanvas 64x64, sudut); dipotong (24, 24, 40, 40)
ICON_DRAW = {
    "scroll": ("scroll_rolled", {}, (32, 32), -35),
    "oldscroll": ("scroll_rolled", {}, (32, 32), 35),
    "book": ("book_closed", {"cover": ("D", "le2")}, (32, 37), 0),
    "lawbook": ("book_closed", {"sym": "law", "cover": ("le1", "le2")}, (32, 37), 0),
    "flask": ("flask", {"bubble": 2}, (32, 38), 0),
    "formula": ("mini_board", {}, (32, 32), 0),
    "laptop": ("mini_laptop", {}, (32, 33), 0),
    "calculator": ("calculator", {}, (32, 38), 0),
    "notebook": ("notebook", {}, (32, 37), 0),
    "network": ("mini_network", {}, (32, 32), 0),
    "wrench": ("wrench", {}, (27, 36), -45),
    "magnifier": ("magnifier", {}, (27, 37), -45),
    "sword": ("sword", {}, (26, 38), -45),
    "axe": ("axe", {}, (27, 38), -60),
    "telescope": ("telescope", {}, (26, 36), -30),
    "star": ("mini_star", {}, (32, 32), 0),
    "papers": ("papers", {}, (32, 37), 0),
    "question": ("mini_question", {}, (32, 32), 0),
    "flag": ("flag", {"wave": 0.0}, (27, 38), -60),
}


def _norm(text):
    return " " + re.sub(r"[^0-9a-zà-ÿ'\-]+", " ", (text or "").lower()) + " "


def _hits(text, kw):
    return len(re.findall(r"(?<![0-9a-zà-ÿ])" + re.escape(kw) + r"(?![0-9a-zà-ÿ])", text))


def scores(text):
    t = _norm(text)
    out = {}
    for dom, (_, _, kws) in DOMAINS.items():
        s = 0
        for kw in kws:
            n = _hits(t, kw)
            if n:
                s += n * (2 if " " in kw else 1)
        if s:
            out[dom] = s
    return out


def select(topic, extra=""):
    """Pilih satu karakter primer dan paling banyak satu aksesori sekunder untuk sebuah topik."""
    sc = scores(topic + " " + (extra or ""))
    ranked = sorted(sc.items(), key=lambda kv: (-kv[1], list(DOMAINS).index(kv[0])))
    if not ranked:
        return {"primary": DEFAULT, "primary_domain": None, "secondary": None, "accessory": None, "scores": {},
                "reason": "tidak ada domain yang cocok: karakter default"}
    pdom = ranked[0][0]
    primary = DOMAINS[pdom][0]
    secondary, acc = None, None
    for dom, s in ranked[1:]:
        if DOMAINS[dom][0] != primary:
            secondary, acc = dom, DOMAINS[dom][1]
            break
    reason = "primer %s (skor %d)" % (pdom, ranked[0][1])
    if secondary:
        reason += ", sekunder %s (skor %d) sebagai aksesori %s" % (secondary, sc[secondary], acc)
    return {"primary": primary, "primary_domain": pdom, "secondary": secondary, "accessory": acc, "scores": sc,
            "reason": reason}


def cast_for(topic, texts, roles=ROLES):
    """Karakter untuk tiap teks petarung: domain teks itu sendiri, lalu domain topik, lalu default."""
    base = select(topic)
    out = []
    for txt in texts:
        s = select(txt)
        if s["primary"] == DEFAULT:
            s = dict(base, reason="ikut topik: " + base["reason"])
        out.append(s)
    return out


def write_json(path):
    data = {"default": DEFAULT, "roles": ROLES,
            "domains": {d: {"character": c, "accessory": a, "keywords": k} for d, (c, a, k) in DOMAINS.items()}}
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
