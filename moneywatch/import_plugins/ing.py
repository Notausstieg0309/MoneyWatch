import re


def parse_csv(stream, name):

    lines = stream.read().decode("latin-1").split('\n')

    # go back to begin of file
    stream.seek(0)

    csv_type = get_csv_type(stream)

    account = None

    for item in lines:
        if item.startswith("IBAN;"):
            account = normalize_iban(re.split('"?;"?',item)[1])
            break

    parsing = False

    result = []

    for item in lines:
        if not parsing:
            if item.startswith("Buchung;Valuta"):
                parsing = True
                continue

        if parsing and item.strip():
            result_item = {}

            columns = re.split('"?;"?', item)

            date = columns[0]
            full_text = columns[2] + " " + columns[3] + " " + columns[4]
            valuta = ""

            if csv_type == "without_saldo":
                valuta = columns[5]
            elif csv_type == "with_saldo":
                valuta = columns[7]

            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date):  # german format
                result_item['date'] = get_date_from_string(columns[0], '%d.%m.%Y')
            elif re.match(r"^\d\d\/\d\d\/\d\d\d\d$", date):  # american format
                result_item['date'] = get_date_from_string(columns[0], '%m/%d/%Y')

            result_item['full_text'] = full_text.strip()
            result_item['valuta'] = float(valuta.replace(",", "."))

            if account:
                result_item['account'] = account

            result.append(result_item)

    return result


def get_csv_type(stream):

    content = stream.read().decode("latin-1")

    items = content.split("\n")


    for item in items:

        if item.startswith("Saldo;"):
            return "with_saldo"

        if item.startswith("Buchung;Valuta;Auftraggeber"):
            return "without_saldo"

    return None


def check_csv(stream, name):
    if get_csv_type(stream) is not None:
        return True
    return False


# register plugin
plugin_info["ing_de_csv"] = {
    "description": "ING.de CSV",
    "parse_function": parse_csv,
    "check_function": check_csv,
    "file_extension": ".csv"
}
