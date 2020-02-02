import re

def parse_csv(stream, name):

    lines = stream.read().decode("latin-1").split('\n')
    
    # go back to begin of file
    stream.seek(0)
    
    type = get_csv_type(stream)

    items = []
    
    # extract IBAN from 4th row second column
    account = normalize_iban(re.split('"?;"?', lines[3])[1])
    
    if type == "without_saldo":
        items = lines[14:]
    elif type == "with_saldo":
        items = lines[15:]
        
        
    result = []
    
    for item in items:
        
        if item.strip():
            result_item = {}
            
            columns = re.split('"?;"?', item)
            
            date = columns[0]
            full_text = columns[2] + " " + columns[4]
            valuta = ""
            
            if type == "without_saldo":            
                valuta = columns[5]
            elif type == "with_saldo":
                valuta = columns[7]
            

            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date): # german format
                result_item['date'] = get_date_from_string(columns[0], '%d.%m.%Y')
            elif re.match(r"^\d\d\/\d\d\/\d\d\d\d$", date): # american format
                result_item['date'] = get_date_from_string(columns[0], '%m/%d/%Y')
                
            result_item['full_text'] = full_text
            result_item['valuta'] = float(valuta.replace(",","."))
            result_item['account'] = account
             
            result.append(result_item)

    return result

def get_csv_type(stream):
    
    
    content = stream.read().decode("latin-1")
    
    items = content.split("\n")
    
    try:
        if items[3].startswith("IBAN;"): 
            
            if not is_valid_iban(re.split('"?;"?', items[3])[1]):
                return None
            
            if items[13].startswith("Buchung;Valuta;Auftraggeber"):
                return "without_saldo"
            elif items[14].startswith("Buchung;Valuta;Auftraggeber"):
                return "with_saldo"
    
    except IndexError as e:
        pass
    
    return None
        
def check_csv(stream, name):    
    if get_csv_type(stream) is not None:
        return True
    return False
    
    
# register plugin    
plugin_info["ing_de_csv"] = {   "description": "ING.de CSV",
                                "parse_function": parse_csv,
                                "check_function": check_csv,
                                "file_extension": ".csv"
                            }
