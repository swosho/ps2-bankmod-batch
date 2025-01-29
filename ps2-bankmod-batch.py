import os
import sys
import struct

def get_u16_le(buf, offset):
    return struct.unpack("<H", buf[offset:offset+2])[0]

def get_u16_be(buf, offset):
    return struct.unpack(">H", buf[offset:offset+2])[0]

def get_u32_le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]

def get_u32_be(buf, offset):
    return struct.unpack(">I", buf[offset:offset+4])[0]

def put_u16_le(buf, offset, value):
    buf[offset:offset+2] = struct.pack("<H", value)

def put_u16_be(buf, offset, value):
    buf[offset:offset+2] = struct.pack(">H", value)

def put_u32_le(buf, offset, value):
    buf[offset:offset+4] = struct.pack("<I", value)

def put_u32_be(buf, offset, value):
    buf[offset:offset+4] = struct.pack(">I", value)

def get_vag_param_offset(hdbuf, vagi_chunk_offset, index):
    return get_u32_le(hdbuf, vagi_chunk_offset + 0x10 + (index * 4))

def get_vag_offset(hdbuf, vagi_chunk_offset, index):
    return get_u32_le(hdbuf, vagi_chunk_offset + get_vag_param_offset(hdbuf, vagi_chunk_offset, index) + 0x00)

def get_vag_sample_rate(hdbuf, vagi_chunk_offset, index):
    return get_u16_le(hdbuf, vagi_chunk_offset + get_vag_param_offset(hdbuf, vagi_chunk_offset, index) + 0x04)

def put_vag_offset(hdbuf, vagi_chunk_offset, index, vag_offset):
    put_u32_le(hdbuf, vagi_chunk_offset + get_vag_param_offset(hdbuf, vagi_chunk_offset, index) + 0x00, vag_offset)

def put_vag_sample_rate(hdbuf, vagi_chunk_offset, index, sample_rate):
    put_u16_le(hdbuf, vagi_chunk_offset + get_vag_param_offset(hdbuf, vagi_chunk_offset, index) + 0x04, sample_rate)

def isnum(n):
    try:
        int(n)
    except ValueError:
        return False
    return True

def extract(hd_path, bd_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(hd_path, "rb") as hd:
        hdbuf = bytearray(hd.read())
    with open(bd_path, "rb") as bd:
        bdbuf = bytearray(bd.read())

    if hdbuf[0x00:0x08] != b"IECSsreV":
        print("Unexpected ID at 0x00 in .HD")
        return
    if hdbuf[0x10:0x18] != b"IECSdaeH":
        print("Unexpected ID at 0x10 in .HD")
        return

    bd_size = get_u32_le(hdbuf, 0x20)
    vagi_chunk_offset = get_u32_le(hdbuf, 0x30)
    max_vag_index = get_u32_le(hdbuf, vagi_chunk_offset + 0x0C)

    for vag_index in range(max_vag_index + 1):
        vag_offset = get_vag_offset(hdbuf, vagi_chunk_offset, vag_index)
        if vag_index < max_vag_index:
            vag_size = get_vag_offset(hdbuf, vagi_chunk_offset, vag_index + 1) - vag_offset
        else:
            vag_size = bd_size - vag_offset
        sample_rate = get_vag_sample_rate(hdbuf, vagi_chunk_offset, vag_index)
        header = bytearray(0x30)
        header[0x00:0x04] = b"VAGp"
        put_u32_be(header, 0x04, 0x20)
        put_u32_be(header, 0x0C, vag_size)
        put_u32_be(header, 0x10, sample_rate)
        with open(os.path.join(out_dir, f"{vag_index:03}.vag"), "wb") as vag:
            vag.write(header + bdbuf[vag_offset:vag_offset + vag_size])

def import_vag(hd_path, bd_path, in_dir):
    for filename in sorted(os.listdir(in_dir)):
        if filename.endswith(".vag"):
            with open(hd_path, "rb") as hd:
                hdbuf = bytearray(hd.read())
            with open(bd_path, "rb") as bd:
                bdbuf = bytearray(bd.read())

            if hdbuf[0x00:0x08] != b"IECSsreV":
                print("Unexpected ID at 0x00 in .HD")
                return
            if hdbuf[0x10:0x18] != b"IECSdaeH":
                print("Unexpected ID at 0x10 in .HD")
                return

            bd_size = get_u32_le(hdbuf, 0x20)
            vagi_chunk_offset = get_u32_le(hdbuf, 0x30)
            max_vag_index = get_u32_le(hdbuf, vagi_chunk_offset + 0x0C)

            vag_index = int(filename.split(".")[0])
            in_vag_path = os.path.join(in_dir, filename)
            with open(in_vag_path, "rb") as in_vagf:
                in_vag_header = in_vagf.read(0x30)
                in_adpcm_buf = in_vagf.read()
                in_adpcm_size = len(in_adpcm_buf)
                in_vag_rate = get_u32_be(in_vag_header, 0x10)

            if vag_index > max_vag_index:
                print(f"Specified sample index {vag_index} exceeds max index")
                continue

            target_vag_offset = get_vag_offset(hdbuf, vagi_chunk_offset, vag_index)
            if vag_index < max_vag_index:
                target_vag_size = get_vag_offset(hdbuf, vagi_chunk_offset, vag_index + 1) - target_vag_offset
            else:
                target_vag_size = bd_size - target_vag_offset

            put_vag_sample_rate(hdbuf, vagi_chunk_offset, vag_index, in_vag_rate)

            for sub_vag_index in range(vag_index + 1, max_vag_index + 1):
                sub_vag_offset = get_vag_offset(hdbuf, vagi_chunk_offset, sub_vag_index)
                put_vag_offset(hdbuf, vagi_chunk_offset, sub_vag_index, (sub_vag_offset - target_vag_size) + in_adpcm_size)

            put_u32_le(hdbuf, 0x20, (bd_size - target_vag_size) + in_adpcm_size)

            with open(hd_path, "wb") as hd:
                hd.write(hdbuf)
            with open(bd_path, "wb") as bd:
                bd.write(bdbuf[:target_vag_offset])
                bd.write(in_adpcm_buf)
                bd.write(bdbuf[target_vag_offset + target_vag_size:bd_size])
                bd.truncate()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage:")
        print("  ps2-bankmod-batch.py -e <INPUT.hd> <INPUT.bd> <OutputDirectory>")
        print("  ps2-bankmod-batch.py -i <INPUT.hd> <INPUT.bd> <ImportsDirectory>")
        sys.exit(1)

    mode = sys.argv[1]
    hd_path = sys.argv[2]
    bd_path = sys.argv[3]
    directory = sys.argv[4]

    if mode == "-e":
        extract(hd_path, bd_path, directory)
    elif mode == "-i":
        import_vag(hd_path, bd_path, directory)
    else:
        print("Invalid mode. Use -e for extraction or -i for import.")
        sys.exit(1)
