import sys
import struct
import xml.etree.ElementTree as ET

def extract_c_string(data, offset):
    end = offset
    while end < len(data) and data[end] != 0:
        end += 1
    return data[offset:end].decode("ascii", errors="replace")

def parse_bseq_header(data):
    fmt = "<4sIHHHHHHHHHHHHIIIIII"
    unpacked = struct.unpack(fmt, data[:struct.calcsize(fmt)])
    return {
        "nameTableOffset": unpacked[18],
        "numSectionBlock": unpacked[12]
    }

def parse_section_block_struct(data, offset):
    fmt = "<bBHIHHHbHB"
    unpacked = struct.unpack(fmt, data[offset:offset+struct.calcsize(fmt)])

    block_offset_fixed = struct.unpack(
        "<H",
        struct.pack(">H", unpacked[8])
    )[0]

    return {
        "sequenceId": unpacked[3],
        "sectionBlockNameTableOffset": unpacked[4],
        "blockType": unpacked[7],
        "blockOffset": block_offset_fixed
    }

def parse_subsection_list_block(data, base_offset):
    num = struct.unpack("<H", data[base_offset:base_offset+2])[0]
    entries = []
    start = base_offset + 4
    for i in range(num):
        off = start + i*8
        seqId, _ = struct.unpack("<IH", data[off:off+6])
        entries.append(seqId)
    return entries

def parse_sequence_flow(data, base_offset):
    num = struct.unpack("<H", data[base_offset:base_offset+2])[0]
    start = base_offset + 4
    flows = []
    for i in range(num):
        off = start + i*8
        flows.append(struct.unpack("<HHHH", data[off:off+8]))
    return flows

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def main():

    if len(sys.argv) != 3:
        print("Usage: python export_sequence_flow_xml.py input.bss output.xml")
        return

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    header = parse_bseq_header(data)

    section_offsets = [
        struct.unpack("<I", data[0x34 + i*4:0x38 + i*4])[0]
        for i in range(header["numSectionBlock"])
    ]

    # sequenceId → SectionBlock name map
    section_map = {}

    for off in section_offsets:
        sb = parse_section_block_struct(data, off)
        name = extract_c_string(
            data,
            header["nameTableOffset"] + sb["sectionBlockNameTableOffset"]
        )
        section_map[sb["sequenceId"]] = name

    root = ET.Element("SequenceFlows")

    for off in section_offsets:

        sb = parse_section_block_struct(data, off)

        if sb["blockType"] not in [2,3]:
            continue

        block_base = off + sb["blockOffset"]

        subsection_offset = struct.unpack("<H", data[block_base+4:block_base+6])[0]
        flow_offset = struct.unpack("<H", data[block_base+6:block_base+8])[0]

        subsection_list = parse_subsection_list_block(
            data,
            block_base + subsection_offset
        )

        flows = parse_sequence_flow(
            data,
            block_base + flow_offset
        )

        section_elem = ET.SubElement(
            root,
            "SectionBlock",
            name=section_map.get(sb["sequenceId"], "UNKNOWN"),
            sequenceId=f"0x{sb['sequenceId']:08X}"
        )

        for f in flows:

            prevIdx, prevRet, nextIdx, nextRet = f

            prevName = "INVALID"
            if prevIdx < len(subsection_list):
                prevSeqId = subsection_list[prevIdx]
                prevName = section_map.get(prevSeqId, "UNKNOWN")

            nextName = "INVALID"
            if nextIdx < len(subsection_list):
                nextSeqId = subsection_list[nextIdx]
                nextName = section_map.get(nextSeqId, "UNKNOWN")

            ET.SubElement(
                section_elem,
                "FlowEntry",
                prevSubsectionListBlockEntryIndex=str(prevIdx),
                prevSubsectionName=prevName,
                prevReturnCodeItemIndex=str(prevRet),
                nextSubsectionListBlockEntryIndex=str(nextIdx),
                nextSubsectionName=nextName,
                nextReturnCodeItemIndex=str(nextRet)
            )

    indent(root)

    tree = ET.ElementTree(root)
    tree.write(sys.argv[2], encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()