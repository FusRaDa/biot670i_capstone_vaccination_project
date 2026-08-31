import re
import us


def translate_state(sas_text):

    # Get STATE value block
    match = re.search(
        r"value\s+STATE\b(.*?);",
        sas_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    state_block = match.group(1)

    # Extract number = "STATE NAME"
    pairs = re.findall(
        r'(\d+)\s*=\s*"([^"]+)"',
        state_block
    )

    # these are exceptions since the US library doesn't pick up on them
    name_fixes = {
        "DISTRICT OF COLUMBIA": "DC",
        "U.S.  VIRGIN ISLANDS": "VI",
    }

    state_map = {}

    for code, state in pairs:

        if state in name_fixes:
            state_map[int(code)] = name_fixes[state]
            continue

        result = us.states.lookup(state)

        if result:
            state_map[int(code)] = result.abbr
        else:
            print(f"Not found: {code} = {state}")

    return state_map


def parse_dat_to_csv(sas_file_path, dat_file_path, csv_output_path):

    # define the core column names
    names = [
        "SEQNUMHH",
        "PROVWT_D",
        "STRATUM",
        "YEAR",
        "STATE",
        "P_UTDMCV",
    ]

    # parse col locations and save in array
    colspecs = []
    with open(sas_file_path, "r", encoding="latin1") as f:
        sas_text = f.read()


        for name in names:
            match = re.search(
                rf"@\d+\s+{re.escape(name)}\s+\$?\d+(?:\.\d*)?",
                sas_text
            )

            col_loc = match.group()

            numbers = re.findall(r"\d+", col_loc)

            start = int(numbers[0]) - 1
            end = start + int(numbers[1])

            colspecs.append((start, end))

    df = pd.read_fwf(
        dat_file_path,
        colspecs=colspecs,
        names=names,
        na_values=["."]
    )

    # translate STATE
    state_map = translate_state(sas_text)
    df["state"] = df["STATE"].map(state_map)
    df.rename(columns={'YEAR': 'year'}, inplace=True)
    df.drop(columns='STATE', inplace=True)

    # save df as csv
    df.to_csv(csv_output_path, index=False)


parse_dat_to_csv('/home/mrada/Projects/BIOT670I_Capstone_Project/raw/nis/2015/NIS-PUF15.SAS', '/home/mrada/Projects/BIOT670I_Capstone_Project/raw/nis/2015/NISPUF15.DAT', 'test_nis.csv')