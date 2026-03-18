import sys
import struct
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
# AUTHOR: ChatGPT, OpenAI LLC
# COAUTHOR (Kind of): Luigifan27
# DATE OF REVISION: 2026, JANUARY 31st
# REVISION: ver1.0.3
# FILENAME: MK7 BSEQ ViewerGUI

#Research conducted on information discovered, and documented by User "B_squo", this is merely a GUI Based Version of his "MK7_BSEQ_analyzer.py" script made by him.

SECTION_TYPE_ENUM = {
    0: "PAGE",
    1: "TASK",
    2: "DATA_HOLDER",
    3: "SERIAL_SEQUENCE",
    4: "CROSS_FADE_SEQUENCE",
    5: "PARALLEL_SEQUENCE",
    6: "DELEGATE_SEQUENCE",
    7: "SCENE_SEQUENCE_PROXY",
    8: "ROOT"
}

SECTION_BLOCK_TYPE_ENUM = {
    0: "PRACTICAL_SECTION_TASK",
    1: "PRACTICAL_SECTION_PAGE",
    2: "SEQUENCE",
    3: "CROSS_FADE_SEQUENCE",
    4: "SCENE_SEQUENCE_PROXY"
}

# Parsing Functions
def is_string_field(key):
    return key == "magic"

def parse_bseq_header(data):
    fmt = "<4sIHHHHHHHHHHHHIIIIII"
    size = struct.calcsize(fmt)
    unpacked = struct.unpack(fmt, data[:size])
    return {
        "magic": unpacked[0].decode('ascii'),
        "sequenceId": unpacked[1],
        "num8": unpacked[2],
        "numa": unpacked[3],
        "numc": unpacked[4],
        "numSections": unpacked[5],
        "numSerialSequence": unpacked[6],
        "numCrossFadeSequence": unpacked[7],
        "numParallelSequence": unpacked[8],
        "numDelegateSequence": unpacked[9],
        "numSceneSequenceProxy": unpacked[10],
        "numLayers": unpacked[11],
        "numSectionBlock": unpacked[12],
        "numEngineCreator": unpacked[13],
        "offset20": unpacked[14],
        "offset24": unpacked[15],
        "firstSectionBlockOffset": unpacked[16],
        "engineCreatorTableOffset": unpacked[17],
        "nameTableOffset": unpacked[18],
        "sectionBlockArrayOffset": unpacked[19],
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

def parse_practical_section_block(data, base_offset, name_table_offset):
    sbdh = parse_section_block_data_header(data, base_offset)
    class_name = extract_null_terminated_string(data, name_table_offset + sbdh['classNameTableOffset'])
    mode_table_rel_offset = struct.unpack("<H", data[base_offset + 4: base_offset + 6])[0]
    mode_table_offset = base_offset + mode_table_rel_offset
    num_entries, index2, mode_entries = parse_name_table_block(data, mode_table_offset)
    mode_list = []
    for e in mode_entries:
        name = extract_null_terminated_string(data, name_table_offset + e["nameTableOffset"])
        mode_list.append({"index": e["index"], "name": name, "offset": e["offset"]})
    return class_name, mode_list

# GUI Stuff
class BSEQViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mario Kart 7 BSEQ GUI Viewer")
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
        filename = filedialog.askopenfilename(filetypes=[("CTRDash Sequence File", "*.BSS *.BRS")])
        if not filename:
            return
        with open(filename, "rb") as f:
            self.data = f.read()
        self.header, _ = parse_bseq_header(self.data)
        self.name_table_offset = self.header["nameTableOffset"]
        self.populate_tree()

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        # EngineCreators
        ec_parent = self.tree.insert("", "end", text="EngineCreators")
        ecs = parse_engine_creator_table(self.data, self.header["engineCreatorTableOffset"], self.header["numEngineCreator"], self.name_table_offset)
        for ec in ecs:
            text = f"{ec['engineCreatorName']} -> {ec['sceneName']}"
            self.tree.insert(ec_parent, "end", text=text, values=(ec,))

        # SectionBlocks
        sb_parent = self.tree.insert("", "end", text="SectionBlocks")
        num_sections = self.header["numSectionBlock"]
        section_offsets_start = 0x34
        for i in range(num_sections):
            offset = section_offsets_start + i*4
            (sec_off,) = struct.unpack("<I", self.data[offset:offset+4])
            sec_block = parse_section_block_struct(self.data, sec_off)
            section_name = extract_null_terminated_string(self.data, self.name_table_offset + sec_block["sectionBlockNameTableOffset"])
            text = f"{SECTION_TYPE_ENUM.get(sec_block['type'], sec_block['type'])}: {section_name}"
            sb_node = self.tree.insert(sb_parent, "end", text=text, values=(sec_block,))

            # enterCodeTable
            enter_offset = sec_off + sec_block["enterCodeTableOffset"]
            try:
                num_entries, index2, enter_entries = parse_name_table_block(self.data, enter_offset)
                enter_node = self.tree.insert(sb_node, "end", text=f"enterCodeTable ({num_entries} entries)")
                for e in enter_entries:
                    name = extract_null_terminated_string(self.data, self.name_table_offset + e["nameTableOffset"])
                    self.tree.insert(enter_node, "end", text=f"{name} (index 0x{e['index']:X})", values=(e,))
            except:
                pass

            # returnCodeTable
            return_offset = sec_off + sec_block["returnCodeTableOffset"]
            try:
                num_entries, index2, return_entries = parse_name_table_block(self.data, return_offset)
                return_node = self.tree.insert(sb_node, "end", text=f"returnCodeTable ({num_entries} entries)")
                for e in return_entries:
                    name = extract_null_terminated_string(self.data, self.name_table_offset + e["nameTableOffset"])
                    self.tree.insert(return_node, "end", text=f"{name} (index 0x{e['index']:X})", values=(e,))
            except:
                pass

            # PracticalSectionBlock
            btype = sec_block['blockType']
            if btype in [0,1]:
                try:
                    block_data_absolute = sec_off + sec_block["blockOffset"]
                    class_name, mode_list = parse_practical_section_block(self.data, block_data_absolute, self.name_table_offset)
                    class_node = self.tree.insert(sb_node, "end", text=f"className: {class_name}")
                    mode_node = self.tree.insert(class_node, "end", text=f"ModeTable ({len(mode_list)} entries)")
                    for m in mode_list:
                        self.tree.insert(mode_node, "end", text=f"{m['name']} (index 0x{m['index']:X})", values=(m,))
                except:
                    pass

    def on_select(self, event):
        self.details.delete("1.0", tk.END)
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item)["values"]
        if values:
            self.details.insert(tk.END, str(values[0]))

    def run(self):
        self.root.mainloop()

# Shit 2 Run Application
if __name__ == "__main__":
    viewer = BSEQViewer()
    viewer.run()
