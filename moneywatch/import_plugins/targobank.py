import re

def parse_csv(stream, name):

    items = stream.read().decode("latin-1").split('\r\n')
    
    result = []
    
    for item in items:
    
        if item.strip():
            result_item = {}
            
            columns = re.split('"?;"?', item)
            
            date = columns[0]
            full_text = columns[1]
            valuta = columns[2]
            
            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date): # german format
                result_item['date'] = get_date_from_string(columns[0], '%d.%m.%Y')
            elif re.match(r"^\d\d\/\d\d\/\d\d\d\d$", date): # american format
                result_item['date'] = get_date_from_string(columns[0], '%m/%d/%Y')
                
            result_item['full_text'] = full_text
            result_item['valuta'] = float(valuta.replace(",","."))
            
            if result_item['valuta'] == 0 and (result_item['full_text'].startswith("RESERV") or result_item['full_text'].startswith("VORAUSDATIERTE")):
                continue
                
            result.append(result_item)

    return result

    
def check_csv(stream, name):    
    if name.startswith("CHK_"):
        return True
    return False
    
    
# register plugin    
plugin_info["targobank_csv"] = { "description": "Targobank CSV",
                                 "parse_function": parse_csv,
                                 "check_function": check_csv,
                                 "file_extension": ".csv"
                               }
