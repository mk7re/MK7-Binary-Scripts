import sys
import struct

SECTION_TYPE_ENUM = {
    0: "PAGE",
    1: "TASK",
    2: "DATA_HOLDER",
    3: "SERIAL_SEQUENCE",
    4: "PARALLEL_SEQUENCE",
    5: "DELEGATE_SEQUENCE",
    6: "SCENE_SEQUENCE_PROXY",
    7: "ROOT"
}

SECTION_BLOCK_TYPE_ENUM = {
    0: "PRACTICAL_SECTION_TASK",
    1: "PRACTICAL_SECTION_PAGE",
    2: "SEQUENCE",
    3: "SCENE_SEQUENCE_PROXY"
}

def is_string_field(key):
    return key == "magic"

def parse_bseq_header(data):
    fmt = "<4sIHHHHHHHHHHIHBBI"
    size = struct.calcsize(fmt)
    unpacked = struct.unpack(fmt, data[:size])
    return {
        "magic": unpacked[0].decode('ascii'),
        "sequenceId": unpacked[1],
        "num_8": unpacked[2],
        "_num_a": unpacked[3],
        "_num_c": unpacked[4],
        "numSections": unpacked[5],
        "numSerialSequence": unpacked[6],
        "numParallelSequence": unpacked[7],
        "numDelegateSequence": unpacked[8],
        "numSceneSequenceProxy": unpacked[9],
        "numLayers": unpacked[10],
        "numSectionBlock": unpacked[11],
        "engineCreatorTableOffset": unpacked[12],
        "numEngineCreator": unpacked[13],
        "field14": unpacked[14],
        "field15": unpacked[15],
        "nameTableOffset": unpacked[16]
    }, size

def extract_null_terminated_string(data, start_offset):
    end = start_offset
    while end < len(data) and data[end] != 0:
        end += 1
    return data[start_offset:end].decode('ascii', errors='replace')

def parse_name_table_block(data, base_offset):
    fmt = "<HH"
    size = struct.calcsize(fmt)
    chunk = data[base_offset:base_offset+size]
    num_entries, index2 = struct.unpack(fmt, chunk)
    entries = []
    entry_fmt = "<HH"
    entry_size = struct.calcsize(entry_fmt)
    start = base_offset + size
    for i in range(num_entries):
        entry_off = start + i*entry_size
        entry_data = data[entry_off : entry_off+entry_size]
        idx, name_offset = struct.unpack(entry_fmt, entry_data)
        entries.append({"index": idx, "nameTableOffset": name_offset, "offset": entry_off})
    return num_entries, index2, entries

def parse_section_block_struct(data, offset):
    fmt = "<bBHIHHHbHB"
    size = struct.calcsize(fmt)
    chunk = data[offset:offset+size]
    unpacked = struct.unpack(fmt, chunk)
    block_offset_raw = unpacked[8]
    block_offset_fixed = struct.unpack("<H", struct.pack(">H", block_offset_raw))[0]
    return {
        "type": unpacked[0],
        "field1": unpacked[1],
        "field20": unpacked[2],
        "sequenceId": unpacked[3],
        "sectionBlockNameTableOffset": unpacked[4],
        "enterCodeTableOffset": unpacked[5],
        "returnCodeTableOffset": unpacked[6],
        "blockType": unpacked[7],
        "blockOffset": block_offset_fixed,
        "pad2": unpacked[9],
    }

def format_enum(value, enum_dict):
    return enum_dict.get(value, f"{value}")

def parse_engine_creator_table(data, offset, num_entries, name_table_offset):
    entry_fmt = "<HH"
    entry_size = struct.calcsize(entry_fmt)
    entries = []
    for i in range(num_entries):
        entry_off = offset + i * entry_size
        entry_data = data[entry_off: entry_off + entry_size]
        engine_name_offset, scene_name_offset = struct.unpack(entry_fmt, entry_data)
        engine_name = extract_null_terminated_string(data, name_table_offset + engine_name_offset)
        scene_name = extract_null_terminated_string(data, name_table_offset + scene_name_offset)
        entries.append({
            "engineCreatorNameTableOffset": engine_name_offset,
            "sceneNameTableOffset": scene_name_offset,
            "engineCreatorName": engine_name,
            "sceneName": scene_name,
            "offset": entry_off
        })
    return entries

def parse_section_block_data_header(data, offset):
    fmt = "<HH"
    size = struct.calcsize(fmt)
    chunk = data[offset:offset+size]
    field0, classNameTableOffset = struct.unpack(fmt, chunk)
    return {
        "field0": field0,
        "classNameTableOffset": classNameTableOffset,
        "offset": offset
    }

def parse_subsection_list_block(data, base_offset):
    fmt = "<HBB"
    size = struct.calcsize(fmt)
    chunk = data[base_offset:base_offset + size]
    num_entries = struct.unpack("<H", chunk[:2])[0]
    entries = []
    entry_size = 8
    start = base_offset + size
    for i in range(num_entries):
        entry_offset = start + i*entry_size
        entry_data = data[entry_offset : entry_offset + entry_size]
        sequence_id, mode_name_idx = struct.unpack("<IH", entry_data[:6])
        entries.append({
            "sequenceId": sequence_id,
            "modeNameItemIndex": mode_name_idx,
            "offset": entry_offset
        })
    return num_entries, entries

def parse_sequence_block_flow_list(data, base_offset):
    fmt = "<HBB"
    size = struct.calcsize(fmt)
    chunk = data[base_offset:base_offset + size]
    num_entries = struct.unpack("<H", chunk[:2])[0]
    entries = []
    entry_size = 8
    start = base_offset + size
    for i in range(num_entries):
        entry_offset = start + i * entry_size
        entry_data = data[entry_offset : entry_offset + entry_size]
        fields = struct.unpack("<HHHH", entry_data[:8])
        entries.append({
            "prevSubsectionListBlockEntryIndex": fields[0],
            "prevReturnCodeItemIndex": fields[1],
            "nextSubsectionListBlockEntryIndex": fields[2],
            "nextReturnCodeItemIndex": fields[3],
            "offset": entry_offset
        })
    return num_entries, entries

def parse_crossfade_sequence_block_flow_list(data, base_offset):
    fmt = "<HBB"
    size = struct.calcsize(fmt)
    chunk = data[base_offset:base_offset + size]
    num_entries = struct.unpack("<H", chunk[:2])[0]
    entries = []
    entry_size = 12
    start = base_offset + size
    for i in range(num_entries):
        entry_offset = start + i * entry_size
        entry_data = data[entry_offset : entry_offset + entry_size]
        fields = struct.unpack("<HHHHHBB", entry_data[:12])
        entries.append({
            "prevSubsectionListBlockEntryIndex": fields[0],
            "prevReturnCodeItemIndex": fields[1],
            "nextSubsectionListBlockEntryIndex": fields[2],
            "nextReturnCodeItemIndex": fields[3],
            "crossFadeType": fields[4],
            "field5_0xa": fields[5],
            "field6_0xb": fields[6],
            "offset": entry_offset
        })
    return num_entries, entries

def parse_practical_section_block(data, base_offset, name_table_offset):
    sbdh = parse_section_block_data_header(data, base_offset)
    print(f"    PracticalSectionBlock: SectionBlockDataHeader field0=0x{sbdh['field0']:04X}, classNameTableOffset=0x{sbdh['classNameTableOffset']:04X} (offset: 0x{sbdh['offset']:X})")
    class_name = extract_null_terminated_string(data, name_table_offset + sbdh['classNameTableOffset'])
    print(f"    className: {class_name}")

    mode_table_rel_offset = struct.unpack("<H", data[base_offset + 4: base_offset + 6])[0]
    mode_table_offset = base_offset + mode_table_rel_offset
    num_entries, index2, mode_entries = parse_name_table_block(data, mode_table_offset)
    print(f"    modeTable: numEntries=0x{num_entries:X}, index2=0x{index2:X} (offset: 0x{mode_table_offset:X})")
    for e in mode_entries:
        name = extract_null_terminated_string(data, name_table_offset + e["nameTableOffset"])
        print(f"      - index: 0x{e['index']:04X}, nameTableOffset: 0x{e['nameTableOffset']:04X}, name: {name} (offset: 0x{e['offset']:X})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python MK7_BSEQ_analyser.py <bseq_filename>")
        return
    filename = sys.argv[1]
    with open(filename, "rb") as f:
        data = f.read()

    header, header_size = parse_bseq_header(data)

    print("BSEQHeader fields:")
    for k, v in header.items():
        if is_string_field(k):
            print(f"  {k}: {v!r}")
        else:
            print(f"  {k}: 0x{v:X}")
    print("\n")

    name_table_offset = header["nameTableOffset"]

    try:
        engine_creators = parse_engine_creator_table(
            data,
            header["engineCreatorTableOffset"],
            header["numEngineCreator"],
            name_table_offset,
        )
        print(f"EngineCreatorTable entries (count=0x{header['numEngineCreator']:X}):")
        for i, ec in enumerate(engine_creators):
            print(f"  Entry {i} (offset: 0x{ec['offset']:X}):")
            print(f"    engineCreatorNameTableOffset: 0x{ec['engineCreatorNameTableOffset']:X} ({ec['engineCreatorName']})")
            print(f"    sceneNameTableOffset: 0x{ec['sceneNameTableOffset']:X} ({ec['sceneName']})")
    except Exception as e:
        print(f"Error reading EngineCreatorTable: {e}")

    # NEW CHANGE: Section offsets start right after header (0x28)
    section_offsets_start = header_size
    num_sections = header["numSectionBlock"]
    section_offsets = []
    print(f"\nSection offsets (count=0x{num_sections:X}):")
    for i in range(num_sections):
        offset = section_offsets_start + i*4
        off_bytes = data[offset : offset+4]
        (off,) = struct.unpack("<I", off_bytes)
        section_offsets.append(off)
        print(f"  Offset[{i}]: 0x{off:X} (offset in file: 0x{offset:X})")

    print("\nSectionBlocks:")
    for i, off in enumerate(section_offsets):
        sec_block_offset = off
        try:
            sec_block = parse_section_block_struct(data, sec_block_offset)
        except Exception as e:
            print(f"  Entry {i} (Offset: 0x{sec_block_offset:X}): Error parsing SectionBlock: {e}")
            continue

        section_name = "<error reading name>"
        try:
            section_name = extract_null_terminated_string(data, name_table_offset + sec_block["sectionBlockNameTableOffset"])
        except:
            pass

        block_data_absolute = sec_block_offset + sec_block["blockOffset"]
        print(f"  Entry {i} (Offset: 0x{sec_block_offset:X}):")
        print(f"    type: {format_enum(sec_block['type'], SECTION_TYPE_ENUM)} (0x{sec_block['type'] & 0xFF:X})")
        print(f"    field1: 0x{sec_block['field1']:02X}")
        print(f"    field20: 0x{sec_block['field20']:04X}")
        print(f"    sequenceId: 0x{sec_block['sequenceId']:08X}")
        print(f"    sectionBlockNameTableOffset: 0x{sec_block['sectionBlockNameTableOffset']:04X} ({section_name})")
        print(f"    enterCodeTableOffset: 0x{sec_block['enterCodeTableOffset']:04X}")
        print(f"    returnCodeTableOffset: 0x{sec_block['returnCodeTableOffset']:04X}")
        print(f"    blockType: {format_enum(sec_block['blockType'], SECTION_BLOCK_TYPE_ENUM)}")
        print(f"    blockOffset: 0x{sec_block['blockOffset']:04X} (absolute: 0x{block_data_absolute:X})")
        print(f"    pad2: 0x{sec_block['pad2']:02X}")

        enter_offset = sec_block_offset + sec_block["enterCodeTableOffset"]
        try:
            num_entries, index2, enter_entries = parse_name_table_block(data, enter_offset)
            print(f"    enterCodeTable: numEntries=0x{num_entries:X}, index2=0x{index2:X}")
            for e in enter_entries:
                name = extract_null_terminated_string(data, name_table_offset + e["nameTableOffset"])
                print(f"      - index: 0x{e['index']:04X}, name: {name}")
        except Exception as e:
            print(f"      Error reading enterCodeTable: {e}")

        return_offset = sec_block_offset + sec_block["returnCodeTableOffset"]
        try:
            num_entries, index2, return_entries = parse_name_table_block(data, return_offset)
            print(f"    returnCodeTable: numEntries=0x{num_entries:X}, index2=0x{index2:X}")
            for e in return_entries:
                name = extract_null_terminated_string(data, name_table_offset + e["nameTableOffset"])
                print(f"      - index: 0x{e['index']:04X}, name: {name}")
        except Exception as e:
            print(f"      Error reading returnCodeTable: {e}")

        btype = sec_block['blockType']
        try:
            if btype in [0, 1]:
                parse_practical_section_block(data, block_data_absolute, name_table_offset)
            elif btype == 2:
                sbdh = parse_section_block_data_header(data, block_data_absolute)
                print(f"    SectionBlockDataHeader: field0=0x{sbdh['field0']:04X}, classNameTableOffset=0x{sbdh['classNameTableOffset']:04X}")
                class_name = extract_null_terminated_string(data, name_table_offset + sbdh['classNameTableOffset'])
                print(f"    className: {class_name}")

                subsection_offset = struct.unpack("<H", data[block_data_absolute + 4: block_data_absolute + 6])[0]
                flow_offset = struct.unpack("<H", data[block_data_absolute + 6: block_data_absolute + 8])[0]
                print(f"    SequenceBlock: subsectionListOffset=0x{subsection_offset:X}, flowListOffset=0x{flow_offset:X}")

                num_entries, entries = parse_subsection_list_block(data, block_data_absolute + subsection_offset)
                print(f"      SubsectionListBlock: numEntries=0x{num_entries:X}")
                for i2, entry in enumerate(entries):
                    print(f"        {i2}: sequenceId=0x{entry['sequenceId']:08X}, modeNameItemIndex=0x{entry['modeNameItemIndex']:04X}")

                num_entries, entries = parse_sequence_block_flow_list(data, block_data_absolute + flow_offset)
                print(f"      SequenceBlockFlowList: numEntries=0x{num_entries:X}")
                for idx, entry in enumerate(entries):
                    print(f"        Entry {idx}: prevSubsection=0x{entry['prevSubsectionListBlockEntryIndex']:04X}, nextSubsection=0x{entry['nextSubsectionListBlockEntryIndex']:04X}")
            elif btype == 4:
                scene_offset = struct.unpack("<H", data[block_data_absolute : block_data_absolute + 2])[0]
                scene_name = extract_null_terminated_string(data, name_table_offset + scene_offset)
                print(f"    SceneSequenceProxyBlock: sceneNameTableOffset=0x{scene_offset:X} ({scene_name})")
        except Exception as e:
            print(f"    Error parsing block specific data: {e}")

if __name__ == "__main__":
    main()
