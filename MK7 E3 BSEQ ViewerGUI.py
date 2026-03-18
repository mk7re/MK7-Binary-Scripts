import sys
import struct
import tkinter as tk
from tkinter import filedialog, ttk
# AUTHOR: ChatGPT, OpenAI LLC
# COAUTHOR (Kind of): Luigifan27
# DATE OF REVISION: 2026, JANUARY 31st
# REVISION: ver1.0.0
# FILENAME: MK7 E3 BSEQ ViewerGUI

# Research conducted on information discovered, and documented by User "B_squo", this is merely a GUI Based Version of his "MK7_BSEQ_analyser_e3_2010.py" script made by him.

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

# ------------------------------
# PARSING FUNCTIONS
# ------------------------------
def extract_null_terminated_string(data, start_offset):
    end = start_offset
    while end < len(data) and data[end] != 0:
        end += 1
    return data[start_offset:end].decode('ascii', errors='replace')

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

def parse_name_table_block(data, base_offset):
    fmt = "<HH"
    size = struct.calcsize(fmt)
    num_entries, index2 = struct.unpack(fmt, data[base_offset:base_offset+size])
    entries = []
    entry_fmt = "<HH"
    entry_size = struct.calcsize(entry_fmt)
    start = base_offset + size
    for i in range(num_entries):
        entry_data = data[start + i*entry_size : start + (i+1)*entry_size]
        idx, name_offset = struct.unpack(entry_fmt, entry_data)
        entries.append({"index": idx, "nameTableOffset": name_offset, "entryOffset": start + i*entry_size})
    return entries

def parse_engine_creator_table(data, offset, num_entries, name_table_offset):
    entry_fmt = "<HH"
    entry_size = struct.calcsize(entry_fmt)
    entries = []
    for i in range(num_entries):
        entry_data = data[offset + i*entry_size : offset + (i+1)*entry_size]
        engine_offset, scene_offset = struct.unpack(entry_fmt, entry_data)
        engine_name = extract_null_terminated_string(data, name_table_offset + engine_offset)
        scene_name = extract_null_terminated_string(data, name_table_offset + scene_offset)
        entries.append({
            "engineCreatorName": engine_name,
            "sceneName": scene_name,
            "offset": offset + i*entry_size
        })
    return entries

def parse_section_block_struct(data, offset):
    fmt = "<bBHIHHHbHB"
    unpacked = struct.unpack(fmt, data[offset:offset+struct.calcsize(fmt)])
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
        "offset": offset
    }

def parse_practical_section_block(data, base_offset, name_table_offset):
    field0, class_offset = struct.unpack("<HH", data[base_offset:base_offset+4])
    class_name = extract_null_terminated_string(data, name_table_offset + class_offset)
    mode_table_rel = struct.unpack("<H", data[base_offset + 4:base_offset + 6])[0]
    mode_table_offset = base_offset + mode_table_rel
    mode_entries = parse_name_table_block(data, mode_table_offset)
    modes = []
    for e in mode_entries:
        name = extract_null_terminated_string(data, name_table_offset + e["nameTableOffset"])
        modes.append(f"{name} (0x{e['index']:X}, entryOffset=0x{e['entryOffset']:X})")
    return class_name, modes, base_offset, class_offset

def parse_subsection_list_block(data, base_offset):
    num_entries = struct.unpack("<H", data[base_offset:base_offset+2])[0]
    entries = []
    start = base_offset + 4
    for i in range(num_entries):
        entry_data = data[start + i*8: start + (i+1)*8]
        sequence_id, mode_idx = struct.unpack("<IH", entry_data[:6])
        entries.append({"sequenceId": sequence_id, "modeIdx": mode_idx, "offset": start + i*8})
    return entries

def parse_sequence_block_flow_list(data, base_offset):
    num_entries = struct.unpack("<H", data[base_offset:base_offset+2])[0]
    entries = []
    start = base_offset + 4
    for i in range(num_entries):
        f0,f1,f2,f3 = struct.unpack("<HHHH", data[start+i*8:start+i*8+8])
        entries.append({"prevSubsection": f0, "prevReturn": f1, "nextSubsection": f2, "nextReturn": f3, "offset": start+i*8})
    return entries

# ------------------------------
# GUI
# ------------------------------
class BSEQViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mario Kart 3Ds E3 BSEQ GUI Viewer")
        self.root.geometry("1200x600")

        self.data = None
        self.header = None
        self.name_table_offset = None

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.details = tk.Text(self.root)
        self.details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open Sequence File...", command=self.open_file)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CTRDash Sequence File Ver02","*.bss *brs")])
        if not filename:
            return
        with open(filename,"rb") as f:
            self.data = f.read()

        self.header, header_size = parse_bseq_header(self.data)
        self.name_table_offset = self.header["nameTableOffset"]
        self.section_offsets_start = header_size
        self.populate_tree()

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())

        # EngineCreators
        ec_parent = self.tree.insert("", "end", text="EngineCreators")
        ecs = parse_engine_creator_table(self.data, self.header["engineCreatorTableOffset"], self.header["numEngineCreator"], self.name_table_offset)
        for ec in ecs:
            self.tree.insert(ec_parent, "end", text=f"{ec['engineCreatorName']} -> {ec['sceneName']} (offset=0x{ec['offset']:X})")

        # SectionBlocks
        sb_parent = self.tree.insert("", "end", text="SectionBlocks")
        for i in range(self.header["numSectionBlock"]):
            offset_bytes = self.data[self.section_offsets_start + i*4 : self.section_offsets_start + i*4 + 4]
            if len(offset_bytes) < 4:
                continue
            (sec_off,) = struct.unpack("<I", offset_bytes)
            sb = parse_section_block_struct(self.data, sec_off)
            sec_name = extract_null_terminated_string(self.data, self.name_table_offset + sb["sectionBlockNameTableOffset"])
            sb_node = self.tree.insert(sb_parent, "end", text=f"{SECTION_TYPE_ENUM.get(sb['type'], sb['type'])}: {sec_name} (offset=0x{sb['offset']:X})")

            # EnterCodeTable
            enter_offset = sec_off + sb["enterCodeTableOffset"]
            try:
                entries = parse_name_table_block(self.data, enter_offset)
                enter_node = self.tree.insert(sb_node, "end", text=f"EnterCodeTable (offset=0x{enter_offset:X})")
                for e in entries:
                    name = extract_null_terminated_string(self.data, self.name_table_offset + e["nameTableOffset"])
                    self.tree.insert(enter_node, "end", text=f"{name} (index=0x{e['index']:X}, entryOffset=0x{e['entryOffset']:X})")
            except:
                pass

            # ReturnCodeTable
            return_offset = sec_off + sb["returnCodeTableOffset"]
            try:
                entries = parse_name_table_block(self.data, return_offset)
                return_node = self.tree.insert(sb_node, "end", text=f"ReturnCodeTable (offset=0x{return_offset:X})")
                for e in entries:
                    name = extract_null_terminated_string(self.data, self.name_table_offset + e["nameTableOffset"])
                    self.tree.insert(return_node, "end", text=f"{name} (index=0x{e['index']:X}, entryOffset=0x{e['entryOffset']:X})")
            except:
                pass

            # PracticalSectionBlock
            if sb["blockType"] in [0,1]:
                block_abs = sec_off + sb["blockOffset"]
                class_name, modes, block_off, class_off = parse_practical_section_block(self.data, block_abs, self.name_table_offset)
                class_node = self.tree.insert(sb_node, "end", text=f"Class: {class_name} (blockOffset=0x{block_off:X}, classNameOffset=0x{class_off:X})")
                mode_node = self.tree.insert(class_node, "end", text="Modes")
                for m in modes:
                    self.tree.insert(mode_node, "end", text=m)

            # SequenceBlock (blockType==2)
            elif sb["blockType"] == 2:
                block_abs = sec_off + sb["blockOffset"]
                # SubsectionList
                try:
                    subsection_entries = parse_subsection_list_block(self.data, block_abs)
                    sub_node = self.tree.insert(sb_node, "end", text=f"SubsectionListBlock (offset=0x{block_abs:X})")
                    for se in subsection_entries:
                        self.tree.insert(sub_node, "end", text=f"SequenceID=0x{se['sequenceId']:X}, ModeIdx=0x{se['modeIdx']:X} (offset=0x{se['offset']:X})")
                    # FlowList
                    flow_entries = parse_sequence_block_flow_list(self.data, block_abs)
                    flow_node = self.tree.insert(sb_node, "end", text=f"SequenceBlockFlowList (offset=0x{block_abs:X})")
                    for fe in flow_entries:
                        self.tree.insert(flow_node, "end", text=f"prevSub=0x{fe['prevSubsection']:X}, nextSub=0x{fe['nextSubsection']:X} (offset=0x{fe['offset']:X})")
                except:
                    pass

    def on_select(self, event):
        self.details.delete("1.0", tk.END)
        sel = self.tree.selection()
        if sel:
            self.details.insert(tk.END, self.tree.item(sel)["text"])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    viewer = BSEQViewer()
    viewer.run()




