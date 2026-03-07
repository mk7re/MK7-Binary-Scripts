import sys
import struct

CONTROL_SIGHT_TYPE = {
    1: 'DUMMY',
    2: 'DEFAULT',
    3: 'DIV_ROOT',
    4: 'DIV_PART',
}

def read_null_terminated_string(data, offset):
    end = data.find(b'\x00', offset)
    if end == -1:
        return data[offset:].decode('ascii', errors='replace')
    return data[offset:end].decode('ascii', errors='replace')

def parse_bctr(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    endian = '<'

    # === Parse BCTRHeader ===
    BCTR_HEADER_SIZE = 8
    header = struct.unpack(endian + '4sI', data[:BCTR_HEADER_SIZE])
    magic = header[0].decode('ascii')
    field1_0x4 = header[1]
    print(f"BCTRHeader:")
    print(f"  magic: {magic}")
    print(f"  field1_0x4: 0x{field1_0x4:08X}")

    # === Parse BCTRControlInfo ===
    offset = BCTR_HEADER_SIZE
    control_info = struct.unpack(endian + '4H', data[offset:offset + 8])
    offset += 8

    # === Parse BCTRNumData ===
    num_data = struct.unpack(endian + '6H', data[offset:offset + 12])
    numMessageDataResources = num_data[0]
    numTextBox = num_data[1]
    numColumnsMessageIDs = num_data[2]
    numGraphics = num_data[3]
    numControlData = num_data[5]
    offset += 12

    # === Parse BCTROffsetData ===
    offset_data = struct.unpack(endian + '10I', data[offset:offset + 40])
    offset += 40

    name_table_offset = offset_data[9]

    # === Parse BCTRNameTableData and Name Table Strings ===
    name_table_data_offset = name_table_offset
    name_table_data = struct.unpack(endian + 'H2B', data[name_table_data_offset:name_table_data_offset + 4])
    name_table_size = name_table_data[0]
    name_table_strings_offset = name_table_data_offset + 4
    name_table_bytes = data[name_table_strings_offset:name_table_strings_offset + name_table_size]

    def resolve_name_string(offset_in_table):
        if offset_in_table < name_table_size:
            return read_null_terminated_string(name_table_bytes, offset_in_table)
        return '<invalid offset>'

    print(f"BCTRControlInfo:")
    print(f"  filenameOffset: 0x{control_info[0]:04X}")
    print(f"    filename: \"{resolve_name_string(control_info[0])}\"")
    print(f"  classNameOffset: 0x{control_info[1]:04X}")
    print(f"    className: \"{resolve_name_string(control_info[1])}\"")
    layout_type_value = control_info[2]
    if layout_type_value in CONTROL_SIGHT_TYPE:
        enum_str = CONTROL_SIGHT_TYPE[layout_type_value]
        print(f"  layoutType: {enum_str}")
    else:
        print(f"  layoutType: {layout_type_value}")
    print(f"  layoutNameOffset: 0x{control_info[3]:04X}")
    print(f"    layoutName: \"{resolve_name_string(control_info[3])}\"")

    print(f"BCTRNumData:")
    print(f"  numMessageDataResources: 0x{numMessageDataResources:04X}")
    print(f"  numTextBox: 0x{numTextBox:04X}")
    print(f"  numColumnsMessageIDs: 0x{numColumnsMessageIDs:04X}")
    print(f"  numGraphics: 0x{num_data[3]:04X}")
    print(f"  field4_0x8: 0x{num_data[4]:04X}")
    print(f"  numControlData: 0x{numControlData:04X}")

    keys = [
        'messageDataResourcesOffset', 'textboxNameOffset', 'field2_0x8', 'graphicsOffset',
        'field4_0x10', 'controlDataOffset', 'messageIDsOffset', 'field7_0x1c',
        'field8_0x20', 'nameTableDataOffset'
    ]
    print(f"BCTROffsetData:")
    for i, key in enumerate(keys):
        if key == 'messageDataResourcesOffset' and numMessageDataResources == 0:
            print(f"  {key}: Not found")
        elif key == 'textboxNameOffset' and numTextBox == 0:
            print(f"  {key}: Not found")
        elif key == 'graphicsOffset' and numGraphics == 0:
            print(f"  {key}: Not found")
        elif key == 'messageIDsOffset' and (numColumnsMessageIDs == 0 or numControlData == 0):
            print(f"  {key}: Not found")
        elif key == 'controlDataOffset' and numControlData == 0:
            print(f"  {key}: Not found")
        else:
            print(f"  {key}: 0x{offset_data[i]:08X}")

    # === textboxNameData section ===
    textbox_name_data_offset = offset_data[1]
    print(f"\nTextboxNameData Section:")
    if numTextBox == 0:
        print(f"  Not found")
    else:
        try:
            (textbox_name_offset,) = struct.unpack(endian + 'I', data[textbox_name_data_offset:textbox_name_data_offset + 4])
            print(f"  textboxNameOffset: 0x{textbox_name_offset:08X}")
            print(f"  textboxName: \"{resolve_name_string(textbox_name_offset)}\"")
        except:
            print(f"  Invalid textboxNameData offset or read error")

    print(f"\nDetected name table offset: 0x{name_table_offset:X}")

    print(f"BCTRNameTableData:")
    print(f"  nameTableSize: 0x{name_table_size:04X}")
    print(f"  field1_0x2: 0x{name_table_data[1]:02X}")
    print(f"  field2_0x3: 0x{name_table_data[2]:02X}")

    message_data_offset = offset_data[0]
    print(f"\nControlResourceMessageData (messageDataResourcesOffset):")
    if numMessageDataResources == 0:
        print(f"  Not found")
    else:
        for i in range(numMessageDataResources):
            offset_pos = message_data_offset + i * 2
            (msbtFilenameOffset,) = struct.unpack(endian + 'H', data[offset_pos:offset_pos + 2])
            print(f"  Entry {i}: msbtFilenameOffset: 0x{msbtFilenameOffset:04X}")
            print(f"    msbtFilename: \"{resolve_name_string(msbtFilenameOffset)}\"")

    control_data_offset = offset_data[5]
    CONTROL_DATA_SIZE = 0x14

    print(f"\nControlData Section (0x{numControlData:X} entries at offset 0x{control_data_offset:X}):")
    for i in range(numControlData):
        entry_offset = control_data_offset + i * CONTROL_DATA_SIZE
        ctrl = struct.unpack(endian + '2H3fH2B', data[entry_offset:entry_offset + CONTROL_DATA_SIZE])
        print(f"  Entry {i}:")
        print(f"    nameOffset: 0x{ctrl[0]:04X}")
        print(f"      name: \"{resolve_name_string(ctrl[0])}\"")
        print(f"    drawOnBottomScreen: {'true' if ctrl[1] == 1 else 'false'}")
        print(f"    position: ({ctrl[2]:.5f}, {ctrl[3]:.5f}, {ctrl[4]:.5f})")
        print(f"    field3_0x10: 0x{ctrl[5]:04X}")
        print(f"    field4_0x12: 0x{ctrl[6]:02X}")
        print(f"    field5_0x13: 0x{ctrl[7]:02X}")

    messageIDsOffset = offset_data[6]
    print(f"\nMessageIDs Section:")
    if numColumnsMessageIDs == 0 or numControlData == 0:
        print(f"  Not found")
    else:
        for row in range(numControlData):
            row_vals = []
            for col in range(numColumnsMessageIDs):
                entry_offset = messageIDsOffset + 4 * (row * numColumnsMessageIDs + col)
                val = struct.unpack(endian + 'I', data[entry_offset:entry_offset + 4])[0]
                row_vals.append(f"0x{val:08X}")
            print("  " + ", ".join(row_vals))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python MK7_BCTR_analysis.py <file.bctr>")
        sys.exit(1)

    filepath = sys.argv[1]
    parse_bctr(filepath)
