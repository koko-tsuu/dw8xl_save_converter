import pytest
import main_functions 
import helpers

# -----------------------------
# Ensure that files are present in the test_files folder
# -----------------------------

PCSave = "./test_files/pc_corrupted.dat" # magic number modified
PSVSave =  "./test_files/psv.dat"
PS3Save = "./test_files/ps3.BIN"
PS4Save =  "./test_files/ps4.BIN"


print(main_functions.identify_console_type(PCSave))
def test_identify_console_type():
    assert main_functions.identify_console_type(PCSave) == "PC"
    assert main_functions.identify_console_type(PSVSave) == "PSV"
    assert main_functions.identify_console_type(PS3Save) == "PS3"
    assert main_functions.identify_console_type(PS4Save) == "PS4"


# Verify the decrypted content (excluding first 4 bytes)
def test_PC_conversions():
    
    with open(PCSave, "rb") as f:
        data = bytearray(f.read()) 

    ## fixed file with magic number
    data_decrypted = main_functions.set_magic_number(helpers.build_decrypted_file(data), True)

    ## PC -> PS3 -> PC
    PCtoPS3 = main_functions.PCtoPS3(data)
    PS3toPC = main_functions.PS3toPC(PCtoPS3)
    assert data_decrypted == helpers.build_decrypted_file(PS3toPC)

    ## PC -> PS4 -> PC
    PCtoPS4 = main_functions.PCtoPS4(data)
    PS4toPC = main_functions.PS4toPC(PCtoPS4)
    assert data_decrypted == helpers.build_decrypted_file(PS4toPC)

    ## PC -> PSV -> PC
    PCtoPSV = main_functions.PCtoPSV(data)
    PSVtoPC = main_functions.PSVtoPC(PCtoPSV)
    assert data_decrypted == helpers.build_decrypted_file(PSVtoPC)
    

def test_PS3_conversions():
    with open(PS3Save, "rb") as f:
        data = bytearray(f.read()) 

    ## PS3 -> PC -> PS3
    PS3toPC = main_functions.PS3toPC(data)
    PCtoPS3 = main_functions.PCtoPS3(PS3toPC)
    assert data == PCtoPS3

    ## PS3 -> PS4 -> PS3
    PS3toPS4 = main_functions.PS3toPS4(data)
    PS4toPS3 = main_functions.PS4toPS3(PS3toPS4)
    assert data == PS4toPS3

    ## PS3 -> PSV -> PS3
    PS3toPSV = main_functions.PS3toPSV(data)
    PSVtoPS3 = main_functions.PSVtoPS3(PS3toPSV)
    assert data == PSVtoPS3

def test_PS4_conversions():
    with open(PS4Save, "rb") as f:
        data = bytearray(f.read()) 

    ## PS4 -> PC -> PS4
    PS4toPC = main_functions.PS4toPC(data)
    PCtoPS4 = main_functions.PCtoPS4(PS4toPC)
    assert data == PCtoPS4

    ## PS4 -> PS3 -> PS4
    PS4toPS3 = main_functions.PS4toPS3(data)
    PS3toPS4 = main_functions.PS3toPS4(PS4toPS3)
    assert data == PS3toPS4

    ## PS4 -> PSV -> PS4
    PS4toPSV = main_functions.PS4toPSV(data)
    PSVtoPS4 = main_functions.PSVtoPS4(PS4toPSV)
    assert data == PSVtoPS4
   
def test_PSV_conversions():
    with open(PSVSave, "rb") as f:
        data = bytearray(f.read()) 

    ## PSV -> PC -> PSV
    PSVtoPC = main_functions.PSVtoPC(data)
    PCtoPSV = main_functions.PCtoPSV(PSVtoPC)
    assert data == PCtoPSV

    ## PSV -> PS3 -> PSV
    PSVtoPS3 = main_functions.PSVtoPS3(data)
    PS3toPSV = main_functions.PS3toPSV(PSVtoPS3)
    assert data == PS3toPSV

    ## PSV -> PS4 -> PSV
    PSVtoPS4 = main_functions.PSVtoPS4(data)
    PS4toPSV = main_functions.PS4toPSV(PSVtoPS4)
    assert data == PS4toPSV
