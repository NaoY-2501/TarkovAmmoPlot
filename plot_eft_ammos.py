import csv
from datetime import datetime
import statistics
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go

import utils


TEMPLATE = (
    "{}<br>"
    + "PenetrationPower:<b>{}</b> ArmorDamage(%):<b>{}</b> Damage:<b>{}</b><br>"
    + "Accuracy(%):<b>{}</b> Recoil(%):<b>{}</b><br>"
    + "FragmentationChance:<b>{}</b> RicochetChance:<b>{}</b><br>"
    + "Speed(m/s):<b>{}</b> SpecialEffects:<b>{}</b>"
)


def get_weapon_types(soup):
    docs = soup.find_all("span", class_="mw-headline")
    weapon_types = [tag.text for tag in docs]
    return weapon_types


def make_ammo_url(ammo_type):
    ammo_type = ammo_type.replace(" ", "_")
    return f"{utils.BASE_URL}/{ammo_type}"


def load_entity_matching_data():
    with open("data/ammo_names.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=("origin", "abbr"))
        next(reader)
        matching_dict = {line["origin"]: line["abbr"] for line in reader}
    return matching_dict


def rename_columns(df):
    df.columns = [
        "Icon",
        "Name",
        "Damage",
        "PenetrationPower",
        "ArmorDamage(%)",
        "Accuracy(%)",
        "Recoil(%)",
        "FragmentationChance",
        "RicochetChance",
        "Speed(m/s)",
        "SpecialEffects",
        "SoldBy",
    ]


def make_ammo_df(ammo_type):
    ammo_type = ammo_type.strip()
    soup = utils.get_soup(ammo_type)
    ammunition = soup.find("a", title="Ammunition").text
    dfs = utils.make_dfs_from_doc(soup)
    df = dfs[0]
    rename_columns(df)
    ammo_types = [ammo_type for _ in range(len(df))]
    ammos = [ammunition for _ in range(len(df))]
    df["Ammunition"] = ammos
    df["AmmoType"] = ammo_types
    return df


def fillna(df):
    df.fillna({"Accuracy(%)": 0, "Recoil(%)": 0, "SpecialEffects": "-"}, inplace=True)


def clean_damage_point(series: pd.Series) -> List[int]:
    damages = []
    for damage_point in series:
        if isinstance(damage_point, str):
            # dtype of shotgun's ammo damage is always object.
            if "x" in damage_point:
                damage_point = damage_point.split("x")[1]
            damage_point = int(damage_point)
        damages.append(damage_point)
    return damages


def filter_by_ammo_type(df: pd.DataFrame, ammo_type: List[str]) -> pd.DataFrame:
    return df.loc[df["AmmoType"] == ammo_type]


def make_updatemenu_dicts(df: pd.DataFrame, ammo_types: List[str]) -> List[Dict[str, Any]]:
    updatemenu_dicts = []
    for idx, ammo_type in enumerate(ammo_types):
        visible = [False for _ in range(len(ammo_types))]
        visible[idx] = True
        updatemenu_dicts.append(
            {
                "method": "update",
                "label": ammo_type,
                "args": [{"visible": visible}, {"title": ammo_type}],
            }
        )
    return updatemenu_dicts


def get_texts(df: pd.DataFrame) -> List[str]:
    texts = []
    for col, row in df.iterrows():
        texts.append(
            TEMPLATE.format(
                row["Name"],
                row["PenetrationPower"],
                row["ArmorDamage(%)"],
                row["Damage"],
                row["Accuracy(%)"],
                row["Recoil(%)"],
                row["FragmentationChance"],
                row["RicochetChance"],
                row["Speed(m/s)"],
                row["SpecialEffects"],
            )
        )
    return texts


def get_context(df, ammo_name=None) -> Dict[str, Any]:
    if ammo_name:
        df = filter_by_ammo_type(df, ammo_name)
    damages = clean_damage_point(df["Damage"])
    damage_median = statistics.median(damages)
    size = [(damage / damage_median) * 30 for damage in damages]
    texts = get_texts(df)
    return {
        "df": df,
        "damages": damages,
        "size": size,
        "texts": texts,
    }


def make_scatter(ammo_name: str, context: Dict[str, Any], abbr_df: pd.DataFrame, visible=False) -> go.Scatter:
    texts = [abbr_df.loc[abbr_df["origin"] == name]["abbr"].values[0] for name in context["df"]["Name"]]
    return go.Scatter(
        x=context["df"]["PenetrationPower"],
        y=context["df"]["ArmorDamage(%)"],
        hovertext=context["texts"],
        text=texts,
        textfont={"color": "#1f2424"},
        textposition="top center",
        mode="markers+text",
        name=ammo_name,
        marker={"size": context["size"]},
        visible=visible,
        opacity=0.85,
    )

    


def plot(df: pd.DataFrame) -> None:
    # fillna
    fillna(df)

    fig = go.Figure()
    
    # create name-abbr dataframe
    abbr_df = pd.read_csv('data/ammo_names.csv')

    # 7.62x25mm Tokarev
    ammo_name = "7.62x25mm Tokarev"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df, visible=True))
    # 9x18mm Makarov
    ammo_name = "9x18mm Makarov"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 9x19mm Parabellum
    ammo_name = "9x19mm Parabellum"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 9x21mm Gyurza
    ammo_name = "9x21mm Gyurza"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # .45 ACP
    ammo_name = ".45 ACP"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 4.6x30mm HK
    ammo_name = "4.6x30mm HK"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 5.7x28mm FN
    ammo_name = "5.7x28mm FN"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 5.45x39mm
    ammo_name = "5.45x39mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 5.56x45mm NATO
    ammo_name = "5.56x45mm NATO"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 7.62x39mm
    ammo_name = "7.62x39mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 7.62x51mm NATO
    ammo_name = "7.62x51mm NATO"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 7.62x54mmR
    ammo_name = "7.62x54mmR"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 9x39mm
    ammo_name = "9x39mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # .366 TKM
    ammo_name = ".366 TKM"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 12.7x55mm STs-130
    ammo_name = "12.7x55mm STs-130"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 12x70mm
    ammo_name = "12x70mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 20x70mm
    ammo_name = "20x70mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))
    # 23x75mm
    ammo_name = "23x75mm"
    context = get_context(df, ammo_name)
    fig.add_trace(make_scatter(ammo_name, context, abbr_df))

    ammo_types = list(df["AmmoType"].unique())
    updatemenu_dicts = make_updatemenu_dicts(df, ammo_types)
    # ref. https://plotly.com/python/reference/layout/updatemenus/
    updatemenus = [
        {
            "buttons": updatemenu_dicts,
            "active": 0,
            "type": "dropdown",
            "bgcolor": "#fefefe",
            "font": {"color": "#1f2424"},
        }
    ]
    fig.update_layout(
        title=ammo_types[0],
        xaxis_title="PenetrationPower",
        yaxis_title="ArmorDamage(%)",
        updatemenus=updatemenus,
        height=900,
        paper_bgcolor="#1f2424",
        font={"color": "#fefefe"}
    )
    fig.write_html(
        "templates/ammo_plot.html",
        full_html=False,
        include_plotlyjs=False,
    )


def main() -> None:
    load_entity_matching_data()
    path = "Ammunition"
    soup = utils.get_soup(path)
    ammo_types = utils.retrieve_ammo_types(soup)
    base_df = make_ammo_df(ammo_types[0])
    for ammo_type in ammo_types[1:]:
        if ammo_type in ["12.7x108mm", "30x29mm", "40x46 mm"]:
            # TODO: HMG, Grenade launcher
            continue
        df = make_ammo_df(ammo_type)
        base_df = base_df.append(df)
    plot(base_df)
    print(f"Finished. {datetime.now()}")


if __name__ == "__main__":
    main()
