import os
from helpers import build_encrypted_file, build_decrypted_file, build_encrypted_file_onlystage4, build_decrypted_file_onlystage4, prepend_4_zero_bytes, remove_first_4_bytes, pad_to_size, truncate, set_magic_number



# -----------------------------
# TYPE -> TYPE CONVERT + ENCRYPTION/DECRYPTION
# -----------------------------

    # Notes:
    # PC: addtl encryption, B7F48
    # PS3: encrypted, B7F44
    # PS4: unencrypted, D0F44
    # PSVITA: unencrypted, B7F44


def identify_console_type(filename):
    try:
        # Checks the file offset to identify the console type
        with open(filename, 'rb') as f:
            f.seek(0, os.SEEK_END)  # Move to the end of the file
            last_offset = f.tell() 

        # +1 for actual EOF
        if (last_offset == 0xB7F48 + 0x1):
            return "PC"
        
        # either PS3 or PSV
        elif (last_offset == 0xB7F44 + 0x1):

            # PS3's magic number is encrypted, PSV's not
            magic_num = [0xF0, 0x02, 0x10, 0x13, 0x09]

            with open(filename, 'rb') as f:
                data = bytearray(f.read())

            for i in range(5):
                if (data[0x0+i] != magic_num[i]):
                    return "PS3"
                    
            return "PSV"
        
        elif (last_offset == 0xD0F44 + 0x1):
            return "PS4"
        
        return ""
        
    except: 
        return ""
        


def convert(input_path, output_path, input_type, output_type):
    with open(input_path, "rb") as f:
        data = bytearray(f.read())

    if input_type == "PC":
        if output_type == "PS3":
            data = PCtoPS3(data)

        elif output_type == "PS4":
            data = PCtoPS4(data)
        
        elif output_type == "PSV":
            data = PCtoPSV(data)

    elif input_type == "PS3":
        if output_type == "PC":
            data = PS3toPC(data)

        elif output_type == "PS4":
            data = PS3toPS4(data)
        
        elif output_type == "PSV":
            data = PS3toPSV(data)

    elif input_type == "PS4":
        if output_type == "PC":
            data = PS4toPC(data)

        elif output_type == "PS3":
            data = PS4toPS3(data)

        elif output_type == "PSV":
            data = PS4toPSV(data)

    elif input_type == "PSV":
        if output_type == "PC":
            data = PSVtoPC(data)

        if output_type == "PS3":
            data = PSVtoPS3(data)
        
        elif output_type == "PS4":
            data = PSVtoPS4(data)

    with open(output_path, "wb") as f:
        f.write(data)

def PCtoPS3(data): 
    # PC: addtl encryption, B7F48
    # PS3: encrypted, B7F44
    
    data = build_decrypted_file(data)

    data = set_magic_number(data, True)

    data = build_encrypted_file_onlystage4(data)

    data = remove_first_4_bytes(data)

    return data



def PCtoPS4(data):
    # PC: addtl encryption, B7F48
    # PS4: unencrypted, D0F44

    # PC save file is encrypted, decrypt it first
    data = build_decrypted_file(data)

    data = set_magic_number(data, True)

    # first 4 bytes are unnecessary + padding
    data = remove_first_4_bytes(data)
    data = pad_to_size(data)

    return data

 
    
def PCtoPSV(data):
    # PC: addtl encryption, B7F48
    # PSVITA: unencrypted, B7F44

    # PC save file is encrypted, decrypt it first
    data = build_decrypted_file(data)

    data = set_magic_number(data, True)

    # first 4 bytes are unnecessary for PSVITA
    data = remove_first_4_bytes(data)

    return data



def PS3toPC(data):
    # PS3: encrypted, B7F44
    # PC: addtl encryption, B7F48
    
    # append
    data = prepend_4_zero_bytes(data)

    data = set_magic_number(data, True)

    # decrypt
    data = build_decrypted_file_onlystage4(data)

    # encrypt
    data = build_encrypted_file(data)

    return data


def PS3toPS4(data):
    # PS3: encrypted, B7F44
    # PS4: unencrypted, D0F44

    data = prepend_4_zero_bytes(data)

    data = set_magic_number(data, True)

    data = build_decrypted_file_onlystage4(data)

    data = remove_first_4_bytes(data)

    data = pad_to_size(data)

    return data


def PS3toPSV(data):
    # PS3: encrypted, B7F44
    # PSVITA: unencrypted, B7F44
    data = prepend_4_zero_bytes(data)
    data = set_magic_number(data, True)
    data = build_decrypted_file_onlystage4(data)
    data = remove_first_4_bytes(data)

    return data




def PS4toPC(data):
    # PS4: unencrypted, D0F44
    # PC: addtl encryption, B7F48

    # truncate
    data = truncate(data, 0xB7F45)
    data = prepend_4_zero_bytes(data)
    data = set_magic_number(data, True)

    # encrypt
    data = build_encrypted_file(data)

    return data

def PS4toPS3(data):
    # PS4: unencrypted, D0F44
    # PS3: encrypted, B7F44
    data = truncate(data, 0xB7F45)
    data = prepend_4_zero_bytes(data)
    data = set_magic_number(data, True)
    data = build_encrypted_file_onlystage4(data)
    data = remove_first_4_bytes(data)

    return data


def PS4toPSV(data):
    # PS4: unencrypted, D0F44
    # PSVITA: unencrypted, B7F44
    data = set_magic_number(data, False)
    data = truncate(data, 0xB7F45)

    return data




def PSVtoPC(data):
    # PSVITA: unencrypted, B7F44
    # PC: addtl encryption, B7F48
    
    # PSVITA's file is already decrypted
    # Append 4 bytes
    data = prepend_4_zero_bytes(data)

    data = set_magic_number(data, True)

    # now we need to encrypt it
    data = build_encrypted_file(data)

    return data


def PSVtoPS3(data):
    # PSVITA: unencrypted, B7F44
    # PS3: encrypted, B7F44
    data = prepend_4_zero_bytes(data)
    data = set_magic_number(data, True)
    data = build_encrypted_file_onlystage4(data)
    data = remove_first_4_bytes(data)

    return data

def PSVtoPS4(data):
    # PSVITA: unencrypted, B7F44
    # PS4: unencrypted, D0F44
 
    # PSVITA's file is already decrypted
    # data only needs to be appended
    data = set_magic_number(data, False)
    data = pad_to_size(data)

    return data




