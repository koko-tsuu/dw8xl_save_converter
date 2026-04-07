MASK32 = 0xFFFFFFFF

def u32(x):
    return x & MASK32



# -----------------------------
# Seed Generation (HEADER)
# -----------------------------

def generate_first_word(data: bytes) -> int:

    DX = 0
    SI = 0

    offset = 4  # start at 5th byte
    count = 0x2DFD1  # number of DWORDs

    for _ in range(count):
        if offset + 4 > len(data):
            break

        low_word  = data[offset] | (data[offset+1] << 8)
        high_word = data[offset+2] | (data[offset+3] << 8)

        DX = (DX + low_word) & 0xFFFF
        SI = (SI + high_word) & 0xFFFF

        offset += 4

    eax = (DX + SI) & 0xFFFFFFFF
    ax = eax & 0xFFFF

    data[0] = ax & 0xFF
    data[1] = (ax >> 8) & 0xFF

    return ax


def generate_second_word() -> int:
    eax = 0x00003039
    eax = u32(eax * 0x41C64E6D + 0x3039)
    eax >>= 16
    return eax & 0xFFFF


def write_seed_header(data: bytearray):
    w1 = generate_first_word(data)
    w2 = generate_second_word()

    data[0] = w1 & 0xFF
    data[1] = (w1 >> 8) & 0xFF
    data[2] = w2 & 0xFF
    data[3] = (w2 >> 8) & 0xFF

    return w1, w2


# -----------------------------
# Helpers
# -----------------------------

def read_u16_le(b, o):
    return b[o] | (b[o+1] << 8)

def read_u32_le(b, o):
    return b[o] | (b[o+1] << 8) | (b[o+2] << 16) | (b[o+3] << 24)

def write_u32_le(b, o, v):
    v &= MASK32
    b[o]   = v & 0xFF
    b[o+1] = (v >> 8) & 0xFF
    b[o+2] = (v >> 16) & 0xFF
    b[o+3] = (v >> 24) & 0xFF


def mix_rounds(val, rounds=3):
    for _ in range(rounds):
        val = u32(val * 0x5B1A7851 + 0xCE4E)
    return val


# -----------------------------
# Stage 1 — DWORD stream XOR
# -----------------------------

def stage1(data: bytearray, rounds=3):
    eax = read_u16_le(data, 2)   # seed from bytes 3–4
    edi = 4                      # start at 5th byte
    count = 0x2DFD1              # number of DWORDs

    for _ in range(count):
        if rounds:
            ecx = rounds
            while ecx:
                eax = u32(eax * 0x5B1A7851 + 0xCE4E)
                ecx -= 1

        val = read_u32_le(data, edi)
        val ^= eax
        write_u32_le(data, edi, val)

        edi += 4




# -----------------------------
# Stage 2 — EOF byte XOR
# -----------------------------

def stage2(data: bytearray, rounds=3):
    ecx = read_u16_le(data, 2)

    while rounds:
        ecx = u32(ecx * 0x5B1A7851 + 0xCE4E)
        rounds -= 1

    offset = 0xB7F48
    data[offset] ^= (ecx & 0xFF)


# -----------------------------
# Stage 4 — Byte-wise LCG XOR, only used for decryption
# -----------------------------

def stage4(data: bytearray):
    ecx = 0x13100200
    edx = 4
    count = 0xB7F44

    for _ in range(count):
        ecx = u32(ecx * 0x41C64E6D + 0x3039)
        al = (ecx >> 16) & 0xFF
        data[edx] ^= al
        edx += 1


# -----------------------------
# Encryption with EOF
# -----------------------------
def stage4_with_eof(data: bytearray):
    eax = 0x13100200  # initial seed
    dl = 0            # running checksum (8-bit)
    
    start = 4
    length = 0xB7F44  # number of bytes encrypted
    end = start + length

    i = start

    # ---- Main loop: process 2 bytes at a time ----
    while i + 1 < end:
        # ---- First byte ----
        cl = data[i]              # original plaintext byte

        eax = u32(eax * 0x41C64E6D + 0x3039)
        ebx = eax
        keystream = (ebx >> 16) & 0xFF

        encrypted = keystream ^ cl
        data[i] = encrypted

        dl = (dl + cl) & 0xFF     # accumulate ORIGINAL byte

        # ---- Second byte ----
        cl = data[i + 1]

        eax = u32(eax * 0x41C64E6D + 0x3039)
        ebx = eax
        keystream = (ebx >> 16) & 0xFF

        encrypted = keystream ^ cl
        data[i + 1] = encrypted

        dl = (dl + cl) & 0xFF

        i += 2

    # ---- If odd leftover byte (rare but handled in asm) ----
    if i < end:
        cl = data[i]

        eax = u32(eax * 0x41C64E6D + 0x3039)
        keystream = (eax >> 16) & 0xFF

        encrypted = keystream ^ cl
        data[i] = encrypted

        dl = (dl + cl) & 0xFF

    # ---- Final EOF byte logic ----
    # add dl, byte ptr [esp+E]   (another accumulator from earlier stage)
    # add dl, cl                 (last CL value from loop)

    # In isolation of this stage, EOF byte is simply DL
    eof_byte = dl & 0xFF
    data[0xB7F48] = eof_byte

    return eof_byte

def remove_first_4_bytes(data: bytearray) -> bytearray:
    """Remove the first 4 bytes."""
    if len(data) < 4:
        raise ValueError("File too small to remove 4 bytes.")

    del data[:4]
    return data


def pad_to_size(data: bytearray, target_size=0xD0F45) -> bytearray:
    """
    Pads the bytearray with 0x00 bytes until it reaches target_size.
    Does nothing if already exactly target_size.
    Raises error if data is larger than target_size.
    """
    current_size = len(data)

    if current_size > target_size:
        raise ValueError(
            f"Data is already larger ({current_size}) than target size ({target_size})."
        )

    if current_size < target_size:
        data.extend(b"\x00" * (target_size - current_size))

    return data



def prepend_4_zero_bytes(data: bytearray) -> bytearray:
    """Insert 4 zero bytes at the start."""
    data[:0] = b"\x00\x00\x00\x00"
    return data



def truncate(data: bytes, max_size=0xB7F40) -> bytearray:
    """
    Truncate file to max_size bytes.
    Default max_size = 0xB7F40
    """
    if len(data) > max_size:
        del data[max_size:]  # truncate in place
    return data

# -----------------------------
# FULL PIPELINE
# -----------------------------

def build_decrypted_file(data):
    print("[*] Running Stage 1 decryption...")
    stage1(data)

    
    print("[*] Running Stage 2 decryption...")
    stage2(data)

    print("[*] Running Stage 4 decryption...")
    stage4(data)


    print("[✓] File decrypted successfully.")

    return data


def build_decrypted_file_onlystage4(data):
    print("[*] Running Stage 4 decryption...")
    stage4(data)


    print("[✓] File decrypted successfully.")

    return data



def build_encrypted_file(data):
    # must be run first, based on order
    print("[*] Running Stage 4 encryption...")
    eof = stage4_with_eof(data)
    print(f"    EOF : {eof:02X}")

    
    print("[*] Generating header seed...")
    w1, w2 = write_seed_header(data)
    print(f"    First word : {w1:04X}")
    print(f"    Second word: {w2:04X}")
    

    print("[*] Running Stage 2 encryption...")
    stage2(data)

    print("[*] Running Stage 1 encryption...")
    stage1(data)


    print("[✓] File encrypted successfully.")


    return data

def build_encrypted_file_onlystage4(data):
    # must be run first, based on order
    print("[*] Running Stage 4 encryption...")
    eof = stage4_with_eof(data)
    print(f"    EOF : {eof:02X}")

    
    print("[✓] File encrypted successfully.")


    return data


# -----------------------------
# When running PC mods, there's a chance that the magic number is modified.
# If modified, game (for other) will think the save file is corrupted when it isn't.
# MAGIC NUMBER: F0 02 10 13 09 
#
# Must be run against unencrypted files.
# -----------------------------

def set_magic_number(data, toOffset):
    magic_num = [0xF0, 0x02, 0x10, 0x13, 0x09]
    offset = 0x0

    if toOffset:
        offset = 0x4

    for i in range(5):
        data[0x0+offset+i] = magic_num[i]

    return data



