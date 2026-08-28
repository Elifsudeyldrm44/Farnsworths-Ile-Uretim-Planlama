import streamlit as st
import pandas as pd
from decimal import Decimal, getcontext

getcontext().prec = 28

st.set_page_config(layout="wide")
st.title("🏭 Üretim Planlama (Çoklu Fabrika)")


# =========================================================
# SAYI BİÇİMLENDİRME
# =========================================================

def sayi_formatla(deger):
    """
    Sayıları binlik ayraç olarak nokta kullanarak gösterir.

    Örnekler:
    6600 -> 6.600
    8300 -> 8.300
    1232 -> 1.232
    1232000 -> 1.232.000
    """

    if deger is None:
        return ""

    try:
        sayi = float(deger)
        return f"{sayi:,.0f}".replace(",", ".")
    except:
        return str(deger)


def sayi_coz(deger):
    """
    Formatlanmış sayıları Python sayısına dönüştürür.

    Örnekler:
    6.600 -> 6600
    8.300 -> 8300
    1.232 -> 1232
    1.232.000 -> 1232000
    """

    if deger is None:
        return 0.0

    deger = str(deger).strip()

    if deger == "":
        return 0.0

    deger = deger.replace(".", "")

    try:
        return float(deger)
    except:
        return 0.0


# =========================================================
# FORMATLANMIŞ GİRİŞ
# =========================================================

def giris_degerini_formatla(anahtar):

    deger = st.session_state.get(
        anahtar,
        ""
    )

    if deger is None:
        return

    deger = str(deger).strip()

    if deger == "":
        return

    try:

        sayi = sayi_coz(deger)

        st.session_state[
            anahtar
        ] = sayi_formatla(sayi)

    except:
        pass


def formatli_sayi_girisi(
    etiket,
    deger,
    anahtar
):

    if anahtar not in st.session_state:

        st.session_state[
            anahtar
        ] = sayi_formatla(deger)

    st.text_input(
        etiket,
        key=anahtar,
        on_change=giris_degerini_formatla,
        args=(anahtar,)
    )

    return sayi_coz(
        st.session_state[anahtar]
    )


# =========================================================
# FABRİKA SAYISI
# =========================================================

fabrika_sayisi = st.number_input(
    "Fabrika Sayısı",
    min_value=1,
    value=2,
    step=1
)

fabrikalar = []


# =========================================================
# FABRİKA GİRDİLERİ
# =========================================================

st.subheader("Fabrika Girdileri")

sutunlar = st.columns(
    fabrika_sayisi
)

for i in range(fabrika_sayisi):

    with sutunlar[i]:

        fabrika_adi = st.text_input(
            f"{i+1}. Fabrika Adı",
            value=f"Fabrika {i+1}",
            key=f"fabrika_adi_{i}"
        )


        # -------------------------------------------------
        # NORMAL ÜRETİM MALİYETİ
        # -------------------------------------------------

        normal_maliyet = formatli_sayi_girisi(
            f"{fabrika_adi} Normal Üretim Maliyeti (TL/Ton)",
            6600,
            anahtar=f"normal_maliyet_{i}"
        )


        # -------------------------------------------------
        # FAZLA MESAİ MALİYETİ
        # -------------------------------------------------

        fazla_mesai_maliyeti = formatli_sayi_girisi(
            f"{fabrika_adi} Fazla Mesai Maliyeti (TL/Ton)",
            9900,
            anahtar=f"fazla_mesai_maliyeti_{i}"
        )


        # -------------------------------------------------
        # NORMAL ÜRETİM KAPASİTESİ
        # -------------------------------------------------

        normal_kapasite = formatli_sayi_girisi(
            f"{fabrika_adi} Normal Üretim Kapasitesi (Ton/Ay)",
            510,
            anahtar=f"normal_kapasite_{i}"
        )


        # -------------------------------------------------
        # FAZLA MESAİ KAPASİTESİ
        # -------------------------------------------------

        fazla_mesai_kapasitesi = formatli_sayi_girisi(
            f"{fabrika_adi} Fazla Mesai Kapasitesi (Ton/Ay)",
            400,
            anahtar=f"fazla_mesai_kapasitesi_{i}"
        )


        # -------------------------------------------------
        # STOK
        # -------------------------------------------------

        stok = formatli_sayi_girisi(
            f"{fabrika_adi} Stok (Ton)",
            75,
            anahtar=f"stok_{i}"
        )


        # -------------------------------------------------
        # HURDA ORANI
        # -------------------------------------------------

        hurda_orani = formatli_sayi_girisi(
            f"{fabrika_adi} Hurda Oranı (%)",
            5,
            anahtar=f"hurda_orani_{i}"
        ) / 100


        fabrikalar.append({

            "adi": fabrika_adi,

            "normal_maliyet":
                normal_maliyet,

            "fazla_mesai_maliyeti":
                fazla_mesai_maliyeti,

            "normal_kapasite":
                normal_kapasite,

            "fazla_mesai_kapasitesi":
                fazla_mesai_kapasitesi,

            "stok":
                stok,

            "hurda":
                hurda_orani
        })


# =========================================================
# FASON ÜRETİM
# =========================================================

st.subheader("Fason Üretim")

fason_maliyeti = formatli_sayi_girisi(
    "Fason Üretim Maliyeti (TL/Ton)",
    15000,
    anahtar="fason_maliyeti"
)

fason_kapasitesi = formatli_sayi_girisi(
    "Fason Üretim Kapasitesi (Ton/Ay)",
    0,
    anahtar="fason_kapasitesi"
)


# =========================================================
# ENFLASYON
# =========================================================

st.subheader("Enflasyon")

enflasyon_uygula = st.checkbox(
    "Enflasyonu Uygula"
)

aylik_enflasyon = formatli_sayi_girisi(
    "Aylık Enflasyon (%)",
    2,
    anahtar="aylik_enflasyon"
)

enflasyon_orani = (
    aylik_enflasyon / 100
)


# =========================================================
# TALEP
# =========================================================

st.subheader("Talep")

varsayilan_talep = pd.DataFrame({

    "Dönem": [

        "Ocak",
        "Şubat",
        "Mart",
        "Nisan",
        "Mayıs",
        "Haziran",
        "Temmuz",
        "Ağustos",
        "Eylül",
        "Ekim",
        "Kasım",
        "Aralık"

    ],

    "Talep": [

        "1.500",
        "1.578",
        "1.670",
        "1.358",
        "1.587",
        "1.581",
        "1.854",
        "3.607",
        "2.066",
        "1.710",
        "1.686",
        "1.794"

    ]
})


# =========================================================
# TALEP TABLOSU FORMATLAMA
# =========================================================

def talep_tablosunu_formatla():

    if "talep_editoru" not in st.session_state:
        return

    veri = st.session_state[
        "talep_editoru"
    ]

    if isinstance(veri, pd.DataFrame):

        veri = veri.copy()

        if "Talep" in veri.columns:

            formatlanmis_degerler = []

            for deger in veri["Talep"]:

                if (
                    deger is None
                    or str(deger).strip() == ""
                ):

                    formatlanmis_degerler.append("")

                    continue

                try:

                    sayi = sayi_coz(deger)

                    formatlanmis_degerler.append(
                        sayi_formatla(sayi)
                    )

                except:

                    formatlanmis_degerler.append(
                        deger
                    )

            veri["Talep"] = (
                formatlanmis_degerler
            )

            st.session_state[
                "talep_editoru"
            ] = veri


# =========================================================
# TALEP TABLOSU
# =========================================================

talep_verisi = st.data_editor(
    varsayilan_talep,
    num_rows="dynamic",
    width="stretch",
    key="talep_editoru",
    on_change=talep_tablosunu_formatla
)


# =========================================================
# SİPARİŞ ERTELEME
# =========================================================

erteleme_isaretleri = []

for i in range(len(talep_verisi)):

    donem_adi = str(
        talep_verisi.loc[
            i,
            "Dönem"
        ]
    )

    if donem_adi.strip() == "":

        erteleme_isaretleri.append(
            False
        )

    else:

        isaret = st.checkbox(
            f"{donem_adi} → Sonraki Döneme Aktar",
            key=f"erteleme_{i}"
        )

        erteleme_isaretleri.append(
            isaret
        )


# =========================================================
# ÜRETİM MODELİ
# =========================================================

def modeli_calistir(
    talep_girdisi,
    senaryo
):

    veri = talep_girdisi.copy()


    # -----------------------------------------------------
    # TALEP DEĞERLERİNİ SAYIYA ÇEVİR
    # -----------------------------------------------------

    veri["Talep"] = (
        veri["Talep"]
        .apply(sayi_coz)
    )

    veri = veri.dropna(
        subset=["Talep"]
    ).reset_index(drop=True)


    # -----------------------------------------------------
    # TALEP SENARYOSU
    # -----------------------------------------------------

    if senaryo == "azalis":

        veri["Talep"] = (
            veri["Talep"]
            * (
                0.9
                ** pd.Series(
                    range(len(veri))
                )
            )
        )

    elif senaryo == "artis":

        veri["Talep"] = (
            veri["Talep"]
            * (
                1.1
                ** pd.Series(
                    range(len(veri))
                )
            )
        )


    sonraki_doneme_aktarilan = 0

    sonuclar = []

    toplam_maliyet = Decimal(0)

    fabrika_durumlari = [

        fabrika.copy()

        for fabrika in fabrikalar

    ]


    # =====================================================
    # DÖNEM HESAPLAMASI
    # =====================================================

    for i in range(len(veri)):

        donem = str(
            veri.loc[
                i,
                "Dönem"
            ]
        )

        if donem.strip() == "":
            continue

        ham_talep = veri.loc[
            i,
            "Talep"
        ]

        if pd.isna(ham_talep):
            continue

        talep = float(
            ham_talep
        )

        talep += (
            sonraki_doneme_aktarilan
        )


        # -------------------------------------------------
        # HURDA DÜZELTMESİ
        # -------------------------------------------------

        ortalama_hurda = (

            sum(
                fabrika["hurda"]
                for fabrika
                in fabrika_durumlari
            )

            / len(
                fabrika_durumlari
            )
        )


        duzeltilmis_talep = (

            talep
            / (
                1 - ortalama_hurda
            )

            if ortalama_hurda < 1

            else talep
        )


        kalan = duzeltilmis_talep


        # -------------------------------------------------
        # ENFLASYON
        # -------------------------------------------------

        enflasyon_carpani = Decimal(1)

        if enflasyon_uygula:

            enflasyon_carpani = (

                Decimal(1)

                + Decimal(
                    str(
                        enflasyon_orani
                    )
                )

            ) ** Decimal(i)


        # -------------------------------------------------
        # GÜNCELLENMİŞ MALİYETLER
        # -------------------------------------------------

        for fabrika in fabrika_durumlari:

            fabrika[
                "normal_maliyet_guncel"
            ] = (

                Decimal(
                    str(
                        fabrika[
                            "normal_maliyet"
                        ]
                    )
                )

                * enflasyon_carpani
            )


            fabrika[
                "fazla_mesai_maliyeti_guncel"
            ] = (

                Decimal(
                    str(
                        fabrika[
                            "fazla_mesai_maliyeti"
                        ]
                    )
                )

                * enflasyon_carpani
            )


        # =================================================
        # STOK
        # =================================================

        stok_sirasi = sorted(

            fabrika_durumlari,

            key=lambda x:
                x[
                    "normal_maliyet_guncel"
                ]
        )

        kullanilan_stok = {}

        for fabrika in stok_sirasi:

            kullanilan = min(

                fabrika["stok"],

                kalan
            )

            kullanilan_stok[
                fabrika["adi"]
            ] = kullanilan

            fabrika["stok"] -= (
                kullanilan
            )

            kalan -= kullanilan

            if kalan <= 0:
                break


        # =================================================
        # NORMAL ÜRETİM
        # =================================================

        normal_uretim_sirasi = sorted(

            fabrika_durumlari,

            key=lambda x:
                x[
                    "normal_maliyet_guncel"
                ]
        )

        kullanilan_normal_uretim = {}

        for fabrika in normal_uretim_sirasi:

            kullanilan = min(

                fabrika[
                    "normal_kapasite"
                ],

                kalan
            )

            kullanilan_normal_uretim[
                fabrika["adi"]
            ] = kullanilan

            kalan -= kullanilan

            if kalan <= 0:
                break


        # =================================================
        # FAZLA MESAİ
        # =================================================

        fazla_mesai_sirasi = sorted(

            fabrika_durumlari,

            key=lambda x:
                x[
                    "fazla_mesai_maliyeti_guncel"
                ]
        )

        kullanilan_fazla_mesai = {}

        for fabrika in fazla_mesai_sirasi:

            kullanilan = min(

                fabrika[
                    "fazla_mesai_kapasitesi"
                ],

                kalan
            )

            kullanilan_fazla_mesai[
                fabrika["adi"]
            ] = kullanilan

            kalan -= kullanilan

            if kalan <= 0:
                break


        # =================================================
        # FASON ÜRETİM
        # =================================================

        fason_kullanimi = min(

            fason_kapasitesi,

            kalan
        )

        kalan -= fason_kullanimi


        # =================================================
        # KARŞILANAMAYAN TALEP
        # =================================================

        acik = max(
            0,
            kalan
        )


        # =================================================
        # SONRAKİ DÖNEME AKTARMA
        # =================================================

        if (

            i < len(veri) - 1

            and erteleme_isaretleri[i]

        ):

            sonraki_doneme_aktarilan = (
                acik
            )

            acik = 0

        else:

            sonraki_doneme_aktarilan = 0


        # =================================================
        # TOPLAM ÜRETİM
        # =================================================

        toplam_uretim = (

            sum(
                kullanilan_stok.values()
            )

            + sum(
                kullanilan_normal_uretim.values()
            )

            + sum(
                kullanilan_fazla_mesai.values()
            )

            + fason_kullanimi

        )


        # =================================================
        # MALİYET HESAPLAMA
        # =================================================

        donem_maliyeti = Decimal(0)

        for fabrika in fabrika_durumlari:

            fabrika_adi = (
                fabrika["adi"]
            )


            # Stok maliyeti
            donem_maliyeti += (

                Decimal(
                    str(
                        kullanilan_stok.get(
                            fabrika_adi,
                            0
                        )
                    )
                )

                * fabrika[
                    "normal_maliyet_guncel"
                ]

            )


            # Normal üretim maliyeti
            donem_maliyeti += (

                Decimal(
                    str(
                        kullanilan_normal_uretim.get(
                            fabrika_adi,
                            0
                        )
                    )
                )

                * fabrika[
                    "normal_maliyet_guncel"
                ]

            )


            # Fazla mesai maliyeti
            donem_maliyeti += (

                Decimal(
                    str(
                        kullanilan_fazla_mesai.get(
                            fabrika_adi,
                            0
                        )
                    )
                )

                * fabrika[
                    "fazla_mesai_maliyeti_guncel"
                ]

            )


        # Fason üretim maliyeti
        donem_maliyeti += (

            Decimal(
                str(
                    fason_kullanimi
                )
            )

            * Decimal(
                str(
                    fason_maliyeti
                )
            )

            * enflasyon_carpani

        )


        toplam_maliyet += (
            donem_maliyeti
        )


        # =================================================
        # SONUÇ SATIRI
        # =================================================

        satir = {

            "Dönem":
                donem,

            "Net Talep":
                talep,

            "Brüt Üretim İhtiyacı":
                duzeltilmis_talep

        }


        # Stok sonuçları
        for fabrika in stok_sirasi:

            satir[
                f"{fabrika['adi']}_Stok"
            ] = kullanilan_stok.get(

                fabrika["adi"],

                0

            )


        # Normal üretim sonuçları
        for fabrika in normal_uretim_sirasi:

            satir[
                f"{fabrika['adi']}_Normal"
            ] = kullanilan_normal_uretim.get(

                fabrika["adi"],

                0

            )


        # Fazla mesai sonuçları
        for fabrika in fazla_mesai_sirasi:

            satir[
                f"{fabrika['adi']}_Fazla Mesai"
            ] = kullanilan_fazla_mesai.get(

                fabrika["adi"],

                0

            )


        satir[
            "Fason Üretim"
        ] = fason_kullanimi

        satir[
            "Açık"
        ] = acik

        satir[
            "Toplam Üretim"
        ] = toplam_uretim

        satir[
            "Maliyet"
        ] = float(
            donem_maliyeti
        )

        sonuclar.append(
            satir
        )


    return (

        pd.DataFrame(sonuclar),

        float(toplam_maliyet)

    )


# =========================================================
# SONUÇLAR
# =========================================================

st.divider()

st.header("Sonuçlar")


sekme1, sekme2, sekme3 = st.tabs([

    "Temel Senaryo",

    "Azalan Talep (-%10)",

    "Artan Talep (+%10)"

])


# =========================================================
# SENARYO SONUÇLARI
# =========================================================

for sekme, senaryo, baslik in [

    (
        sekme1,
        "normal",
        "Temel Senaryo"
    ),

    (
        sekme2,
        "azalis",
        "Azalan Talep"
    ),

    (
        sekme3,
        "artis",
        "Artan Talep"
    )

]:

    with sekme:

        st.subheader(
            baslik
        )


        sonuc, toplam_maliyet = (
            modeli_calistir(
                talep_verisi,
                senaryo
            )
        )


        # -------------------------------------------------
        # TOPLAM MALİYET
        # -------------------------------------------------

        st.metric(

            "Toplam Maliyet",

            sayi_formatla(
                toplam_maliyet
            )

        )


        # -------------------------------------------------
        # SONUÇ TABLOSU
        # -------------------------------------------------

        sayisal_sutunlar = (

            sonuc

            .select_dtypes(
                include="number"
            )

            .columns

        )


        formatlanmis_sonuc = (
            sonuc.style.format({

                sutun:

                    lambda deger:
                        sayi_formatla(
                            deger
                        )

                for sutun
                in sayisal_sutunlar

            })
        )


        # -------------------------------------------------
        # VURGULANACAK SÜTUNLAR
        # -------------------------------------------------

        for sutun in [

            "Toplam Üretim",

            "Maliyet"

        ]:

            if sutun in sonuc.columns:

                formatlanmis_sonuc = (
                    formatlanmis_sonuc.map(

                        lambda deger:
                            "font-weight:bold",

                        subset=[sutun]

                    )
                )


        st.dataframe(

            formatlanmis_sonuc,

            width="stretch"

        )
