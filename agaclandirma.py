# -*- coding: utf-8 -*-
"""
YÖKSİS Birim hiyerarşisini görselleştirme (treemap + sunburst) ve
katlanır metin ağacı olarak gösterim.

Çalıştırma:
    streamlit run agaclandirma.py
"""

import os
from collections import defaultdict
from functools import lru_cache

import pandas as pd
import plotly.express as px  # type: ignore
import pyodbc
import streamlit as st
from dotenv import load_dotenv
from textwrap import dedent
import warnings
from typing import Optional, Any, cast

# Placeholders for type checkers; will be overwritten if SQLAlchemy is available
URL = None  # type: ignore
create_engine = None  # type: ignore
sa_text = None  # type: ignore
_HAS_SQLA = False
try:
    from sqlalchemy.engine import URL as SA_URL
    from sqlalchemy import create_engine as SA_create_engine, text as SA_text
    URL = SA_URL
    create_engine = SA_create_engine
    sa_text = SA_text
    _HAS_SQLA = True
except Exception:
    _HAS_SQLA = False

# ------------------------------------------------------------
# Streamlit temel ayarları
# ------------------------------------------------------------
st.set_page_config(page_title="YÖKSİS Hiyerarşi", layout="wide")
st.title("🌳 YÖKSİS Birim Hiyerarşisi")

# .env yükle
load_dotenv()

# ------------------------------------------------------------
# Bağlantı ayarları ( .env dosyasından )
# ------------------------------------------------------------
DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
SERVER = os.getenv("SQL_SERVER")
DB = os.getenv("SQL_DB")
UID = os.getenv("SQL_UID")
PWD = os.getenv("SQL_PWD")


def connect():
    """pyodbc bağlantısı kurar. Bazı hesaplarda varsayılan DB erişimi kapalı
    olabildiği için doğrudan 'master' veritabanına bağlanıp sorgularda
    üç parçalı ad (DB.dbo.TABLO) kullanacağız.
    """
    missing = [k for k, v in {
        "SQL_SERVER": SERVER,
        "SQL_DB": DB,
        "SQL_UID": UID,
        "SQL_PWD": PWD,
    }.items() if not v]
    if missing:
        st.error(".env içinde eksik değer(ler) var: " + ", ".join(missing))
        st.stop()

    # İlk bağlantıyı master'a yap (login 4060 hatasını önlemek için)
    conn_str = (
        f"DRIVER={{{{}}}};SERVER={SERVER};DATABASE=master;UID={UID};PWD={PWD};"
        f"TrustServerCertificate=yes;".format(DRIVER)
    )
    return pyodbc.connect(conn_str)

def get_sa_engine():
    """Return a SQLAlchemy engine connected to 'master' DB if SQLAlchemy is available; else None."""
    if not _HAS_SQLA:
        return None
    missing = [k for k, v in {
        "SQL_SERVER": SERVER,
        "SQL_DB": DB,
        "SQL_UID": UID,
        "SQL_PWD": PWD,
    }.items() if not v]
    if missing:
        return None
    url = cast(Any, URL).create(
        drivername="mssql+pyodbc",
        username=UID,
        password=PWD,
        host=SERVER,
        database="master",  # login 4060'a karşı master'a bağlan, sorguda [DB] kullanıyoruz
        query={"driver": DRIVER, "TrustServerCertificate": "yes"},
    )
    engine = cast(Any, create_engine)(url, pool_pre_ping=True, fast_executemany=False)
    return engine

def db_exists(conn, db_name: Optional[str]) -> bool:
    if db_name is None:
        return False
    if _HAS_SQLA:
        eng = get_sa_engine()
        if eng is not None:
            with eng.connect() as c:
                row = c.execute(cast(Any, sa_text)("SELECT 1 FROM sys.databases WHERE name = :n"), {"n": db_name}).fetchone()
                return bool(row)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM sys.databases WHERE name = ?", db_name)
    row = cur.fetchone()
    cur.close()
    return bool(row)


def find_similar_tables(conn, db_name: Optional[str], base_name: str = "YoksisBirim"):
    if db_name is None:
        return []
    if _HAS_SQLA:
        try:
            eng = get_sa_engine()
            if eng is not None:
                with eng.connect() as c:
                    rows = c.execute(cast(Any, sa_text)(
                        f"SELECT TABLE_SCHEMA, TABLE_NAME FROM [{db_name}].INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE :pat"
                    ), {"pat": base_name + '%'}).fetchall()
                    return [(r[0], r[1]) for r in rows]
        except Exception:
            pass
    """Return list of (schema, table) in the target DB that resemble the table name."""
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT TABLE_SCHEMA, TABLE_NAME FROM [{db_name}].INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_NAME LIKE ?",
            base_name + '%',
        )
        rows = cur.fetchall()
        cur.close()
        return [(r[0], r[1]) for r in rows]
    except Exception:
        return []


@st.cache_data(ttl=600)
def load_df(only_active: bool) -> pd.DataFrame:
    """dbo.YoksisBirim'den veriyi çeker ve ids/parents formatına getirir."""
    conn = connect()

    # 1) DB var mı?
    if not db_exists(conn, DB):
        cur = conn.cursor()
        cur.execute("SELECT name FROM sys.databases ORDER BY name")
        dbs = [r[0] for r in cur.fetchall()]
        cur.close()
        st.error(
            dedent(
                f"""
                Belirttiğin veritabanı bulunamadı: `{DB}`
                Mevcut veritabanları: {', '.join(dbs)}
                Lütfen `.env` içindeki `SQL_DB` değerini doğru adla değiştir.
                """
            )
        )
        st.stop()

    # 2) Önce üç parçalı adla dene
    q = f"""
        SELECT
          CAST(YoksisId AS varchar(50)) AS id,
          CASE WHEN UstYoksisId IS NULL OR UstYoksisId = 0
               THEN '' ELSE CAST(UstYoksisId AS varchar(50)) END AS parent,
          Ad AS label,
          KisaAd,
          Tur,
          Durum
        FROM [{DB}].dbo.YoksisBirim
        """
    try:
        eng = get_sa_engine()
        if eng is not None:
            # Pandas 2.x uyarısını önlemek için SQLAlchemy engine nesnesini doğrudan kullan
            df = pd.read_sql(q, eng)
        else:
            # Son çare: pyodbc ile devam et; uyarıyı bastır ve type checker'ı rahatlatmak için cast(Any)
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=r"pandas only supports SQLAlchemy connectable",
                    category=UserWarning,
                )
                df = pd.read_sql(q, cast(Any, conn))
    except Exception as e:
        # Şema veya tablo adı farklı olabilir; benzer tabloları gösterelim
        candidates = find_similar_tables(conn, DB, "YoksisBirim")
        if candidates:
            st.error(
                dedent(
                    """
                    Tablo bulunamadı: `[{}].dbo.YoksisBirim`.
                    Bu isimlere benzeyen tablolar tespit edildi:
                    - {}
                    Lütfen doğru şemayı/ismi `.env` veya sorguda güncelleyelim.
                    """.format(DB, "\n                    - ".join([f"{s}.{t}" for s, t in candidates]))
                )
            )
        else:
            st.error(f"Sorgu başarısız oldu: {e}")
        st.stop()

    conn.close()

    # Durum filtresi
    if only_active:
        df = df[df["Durum"].str.lower() == "aktif"]

    # Boş/NaN güvenliği
    df["label"] = df["label"].fillna("")
    df["parent"] = df["parent"].fillna("")

    return df


# ------------------------------------------------------------
# Sidebar filtreleri
# ------------------------------------------------------------
st.sidebar.header("Filtreler")
only_active = st.sidebar.checkbox("Sadece Aktif birimler", value=True)

# (EK) Treemap zoom'unu sıfırla: yeni key ile grafiği baştan çiz
if "tm_key" not in st.session_state: 
    st.session_state.tm_key = 0
# (EK) Geri (Tümünü Göster) — aramayı ve zoom'u sıfırla
# Removed the "Geri (Tümünü Göster)" button and its functionality as per instructions

if st.sidebar.button("↩︎ Zoomu Sıfırla"):
    # Arama filtresi aktifse temizle ve köke dön
    if st.session_state.get("search", "").strip():
        st.session_state["search"] = ""
    st.session_state.tm_key += 1
    st.rerun()

search = st.sidebar.text_input("Ada göre ara", key="search")

# Veri
_df = load_df(only_active)
    
# (EK) Arama metni değiştiğinde treemap zoom'unu da sıfırla
if "prev_search" not in st.session_state:
    st.session_state.prev_search = search
elif st.session_state.prev_search != search:
    st.session_state.prev_search = search
    st.session_state.tm_key += 1
    st.rerun()
if search.strip():
    term = search.strip()
    # 1) Eşleşen düğümler
    match_ids = set(_df[_df["label"].str.contains(term, case=False, na=False)]["id"])
    if match_ids:
        # 2) Ataları ekle
        parent_map = dict(zip(_df["id"], _df["parent"]))
        keep = set(match_ids)
        for mid in list(match_ids):
            cur = mid
            seen = set()
            while parent_map.get(cur):
                if cur in seen:  # döngü koruması
                    break
                seen.add(cur)
                cur = parent_map[cur]
                keep.add(cur)
        # 3) Çocukları ekle
        from collections import defaultdict
        children = defaultdict(list)
        for _id, parent in zip(_df["id"], _df["parent"]):
            if parent:
                children[parent].append(_id)
        def add_desc(start):
            # Döngü/yeniden ziyaret koruması ve recursion yerine iteratif yaklaşım
            seen = set()
            stack = [start]
            while stack:
                n = stack.pop()
                if n in seen:
                    continue
                seen.add(n)
                for c in children.get(n, []):
                    if c not in keep:
                        keep.add(c)
                    if c not in seen:
                        stack.append(c)
        for mid in list(match_ids):
            add_desc(mid)
        _df = _df[_df["id"].isin(keep)].copy()
    else:
        # hiçbir eşleşme yoksa kullanıcıya mesaj göster, veri setini boşaltma
        st.warning("Arama sonucunda eşleşme bulunamadı.")

# ------------------------------------------------------------
# Görsel 1: Treemap
# ------------------------------------------------------------
# Treemap'i soldaki dar sütuna al ve kare boşluğu azalt
left_col, _ = st.columns([3, 1])
with left_col:
    st.subheader("Treemap")
    # disp_label: kutu üstünde kısa ad/etiket, hover'da tam ad
    df_show = _df.copy()
    df_show["disp_label"] = df_show["label"].apply(lambda x: x if len(x) <= 25 else x[:22] + "...")
    fig1 = px.treemap(
        df_show,
        names="disp_label",
        parents="parent",
        ids="id",
        custom_data=["label"],
    )
    # Tam ad hover'da, kutu üstünde disp_label (kısaltılmış) her zaman görünsün
    fig1.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><extra></extra>",
        textinfo="label",
        texttemplate="%{label}",
        textposition="middle center",
    )
    fig1.update_layout(
        # Ana görünümde küçük (alt seviye) kutu yazılarını gizle; fakülteye zoom yapınca alan büyüyünce görünür
        uniformtext=dict(minsize=12, mode='hide'),
        height=900,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig1, use_container_width=True, key=f"tm_{st.session_state.get('tm_key', 0)}")

# ------------------------------------------------------------
# Metin tabanlı katlanır (collapsible) ağaç
# ------------------------------------------------------------
st.subheader("Metin Ağaç")

# (EK) Metin ağacı için Tümünü Aç/Kapat butonları
if "expand_all" not in st.session_state:
    st.session_state.expand_all = False
c1, c2 = st.columns(2)
with c1:
    if st.button("Tümünü Aç"):
        st.session_state.expand_all = True
with c2:
    if st.button("Tümünü Kapat"):
        st.session_state.expand_all = False

@lru_cache(maxsize=None)
def _items_tuple():
    # cache'e uygun olması için tuple'a dönüştür
    return tuple(_df[["id", "parent", "label", "Durum"]].itertuples(index=False, name=None))


def build_children_map(items):
    children = defaultdict(list)
    for _id, parent, label, durum in items:
        children[parent].append({"id": _id, "label": label, "durum": durum})
    for k in children:
        children[k].sort(key=lambda x: x["label"])  # alfabetik
    return children


def render_tree(ch, node_id="", level=0):
    for child in ch.get(node_id, []): 
        prefix = "\u2007" * level  # ince boşluk (figür bozulmasın)
        with st.expander(f"{prefix}• {child['label']}", expanded=st.session_state.get("expand_all", False)):
            st.write(f"**YoksisId:** `{child['id']}`  |  **Durum:** `{child['durum']}`")
            render_tree(ch, child["id"], level + 1)


_children = build_children_map(_items_tuple())
render_tree(_children, "")

# ------------------------------------------------------------
# İpucu / Yardım
# ------------------------------------------------------------
st.info(
    "Arama kutusuna bölüm adının bir kısmını yazıp hem grafiklerde hem de metin ağaçta filtreleyebilirsin.\n"
    "ODBC sürümü makinede farklıysa .env içindeki SQL_DRIVER değerini 17 ile değiştir.\n"
    "Tablo adı/şeması hatası alırsan yukarıdaki uyarıdaki önerilen isimlerden birini kullanalım."
)
