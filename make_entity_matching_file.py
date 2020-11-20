from pathlib import Path

import utils


def extract_ammo_names(ammo_types):
    ammo_names = []
    for ammo_type in ammo_types:
        type_name = ammo_type.replace(" ", "_")
        url = f"{utils.BASE_URL}/{type_name}"
        soup = utils.get_soup(url)
        doc = soup.find("table", class_="wikitable")
        dfs = utils.make_dfs_from_doc(doc)
        names = dfs[0]["Name"].values
        ammo_names.extend(names)
    return ammo_names


def output(ammo_names):
    fname = "data/ammo_names.csv"
    file_path = Path(fname)
    if not file_path.exists():
        with open(fname, "x", encoding="utf-8") as f:
            f.write(f"origin,abbr\n")
            for ammo_name in ammo_names:
                f.write(f"{ammo_name},\n")
    else:
        with open(fname, "r+", encoding="utf-8") as f:
            next(f)
            exist_names = [row.split(",")[0].strip() for row in f.readlines()]
            diffs = set(ammo_names) - set(exist_names)
            if diffs:
                for ammo_name in diffs:
                    f.write(f"{ammo_name},\n")


def make_entity_matching_file():
    path = "Ammunition"
    soup = utils.get_soup(path)
    print(f"Retrieve ammo types from {utils.BASE_URL}/{path}")
    ammo_types = utils.retrieve_ammo_types(soup)
    print("Extract ammo names")
    ammo_names = extract_ammo_names(ammo_types)
    print(f"{len(ammo_names)} names extracted")
    print("output ammo names to ammo_names.csv")
    output(ammo_names)
    print("Done.")


if __name__ == "__main__":
    make_entity_matching_file()
