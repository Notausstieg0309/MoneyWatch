import re

def parse_csv(stream, name):

    is_valuta_re = re.compile(r'^-?\d+[\.,]\d{2}$')

    column_split_re = re.compile(r'["\']?;["\']?')
    items = stream.read().decode("latin-1").split('\r\n')
    
    result = []

    # check if csv file contains 2 columns for faluta
    two_columns_valuta = False

    if items:

        columns = column_split_re.split(items[0])

        if len(columns) == 7: # 2 columns for positive and negative valuta
            two_columns_valuta = True    

    for item in items:
    
        if item.strip():
            result_item = {}
            
            columns = column_split_re.split(item)
   
            date = columns[0]
            full_text = columns[1]

            valuta = None
            
            if two_columns_valuta:
                account = columns[6]

                if columns[2] == "" and is_valuta_re.match(columns[3]) is not None:
                    valuta = columns[3]
                elif columns[3] == "" and is_valuta_re.match(columns[2]) is not None:
                    valuta = columns[2]
                else:
                    raise Exception("unable to determine valuta column")
            else:
                valuta = columns[2]
                account = columns[5]
                
            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date): # european format
                result_item['date'] = get_date_from_string(date, '%d.%m.%Y')
                
            result_item['full_text'] = full_text
            result_item['valuta'] = float(valuta.replace(",","."))
            result_item['account'] = account
            
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
