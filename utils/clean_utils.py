def remove_chars(string, chars):
    translation_table = str.maketrans("", "", chars)
    modified_string = string.translate(translation_table)
    return modified_string

def str_to_list(string, chars_to_strip):
    clean_string = remove_chars(string, chars_to_strip) 
    output_list = [item.strip() for item in clean_string.split(",")] # strips spaces around commas, converts to list
    return output_list