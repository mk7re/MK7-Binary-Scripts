import sys
import struct
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
# AUTHOR: ChatGPT, OpenAI LLC
# COAUTHOR (Kind of): Luigifan27
# DATE OF REVISION: 2026, JANUARY 31st
# REVISION: ver1.0.1
# FILENAME: MK7 BCTR Editor AdvancedGUI

# Research conducted on information discovered, and documented by User "B_squo", this is merely a GUI Based Version of his "MK7_BCTR_Analyzer.py" script made by him/ChatGPT OpenAI.

CONTROL_SIGHT_TYPE = {1:'DUMMY', 2:'DEFAULT', 3:'DIV_ROOT', 4:'DIV_PART'}
CONTROL_DATA_SIZE = 0x14

def read_null_terminated_string(data, offset):
    end = data.find(b'\x00', offset)
    if end == -1:
        return data[offset:].decode('ascii', errors='replace')
    return data[offset:end].decode('ascii', errors='replace')

def write_null_terminated_string(data, offset, string, max_len=None):
    bytes_str = string.encode('ascii') + b'\x00'
    if max_len is not None:
        bytes_str = bytes_str[:max_len].ljust(max_len, b'\x00')
    data[offset:offset+len(bytes_str)] = bytes_str

class BCTRViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mario Kart 7 BCTR Advanced GUI Editor")
        self.root.geometry("1200x700")
        self.data = None
        self.filename = None
        self.name_table_offset = None
        self.num_data = {}
        self.control_data_entries = []
        self.message_ids = []
        self.message_data_resources = []

        # Object reference storage for Treeview
        self.obj_refs = {}
        self.next_obj_id = 0

        # Tree
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Details
        self.details = tk.Text(self.root)
        self.details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Menu
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save BCTR", command=self.save_file)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    # File Ops
    def open_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Binary Control File", "*.bctr")])
        if not self.filename:
            return
        with open(self.filename, "rb") as f:
            self.data = bytearray(f.read())
        self.parse_bctr()
        self.populate_tree()

    def save_file(self):
        if not self.filename or not self.data:
            return
        with open(self.filename, "wb") as f:
            f.write(self.data)
        messagebox.showinfo("Saved", f"Saved changes to {self.filename}")

    # --- Parsing ---
    def parse_bctr(self):
        data = self.data
        endian = '<'

        # Header
        magic, field1_0x4 = struct.unpack(endian+'4sI', data[:8])
        self.header = {"magic":magic.decode('ascii'), "field1_0x4":field1_0x4}

        # ControlInfo
        control_info_raw = struct.unpack(endian+'4H', data[8:16])
        self.control_info = {
            "filenameOffset": control_info_raw[0],
            "classNameOffset": control_info_raw[1],
            "layoutType": CONTROL_SIGHT_TYPE.get(control_info_raw[2], control_info_raw[2]),
            "layoutNameOffset": control_info_raw[3]
        }

        # NumData
        num_data_raw = struct.unpack(endian+'6H', data[16:28])
        self.num_data = {
            "numMessageDataResources": num_data_raw[0],
            "numTextBox": num_data_raw[1],
            "numColumnsMessageIDs": num_data_raw[2],
            "numGraphics": num_data_raw[3],
            "field4_0x8": num_data_raw[4],
            "numControlData": num_data_raw[5]
        }

        # Offsets
        offset_data = struct.unpack(endian+'10I', data[28:68])
        self.offset_data = offset_data
        self.name_table_offset = offset_data[9]

        # MessageDataResources
        self.message_data_resources = []
        msg_data_offset = offset_data[0]
        for i in range(self.num_data["numMessageDataResources"]):
            msbt_off = struct.unpack('<H', data[msg_data_offset + i*2:msg_data_offset + i*2 + 2])[0]
            name = read_null_terminated_string(data, self.name_table_offset + 4 + msbt_off)
            self.message_data_resources.append({
                "name": name,
                "offset_in_file": msg_data_offset + i*2,
                "nameOffset": msbt_off
            })

        # ControlData
        self.control_data_entries = []
        control_data_offset = offset_data[5]
        for i in range(self.num_data["numControlData"]):
            entry_offset = control_data_offset + i*CONTROL_DATA_SIZE
            ctrl = struct.unpack(endian+'2H3fH2B', data[entry_offset:entry_offset+CONTROL_DATA_SIZE])
            name_offset, draw_bottom, x, y, z, f3, f4, f5 = ctrl
            name = read_null_terminated_string(data, self.name_table_offset + 4 + name_offset)
            self.control_data_entries.append({
                "name": name,
                "drawOnBottomScreen": draw_bottom,
                "position": (x,y,z),
                "nameOffset": name_offset,
                "offset_in_file": entry_offset
            })

        # MessageIDs
        self.message_ids = []
        if self.num_data["numColumnsMessageIDs"] > 0 and self.num_data["numControlData"] > 0:
            msg_id_offset = offset_data[6]
            for row in range(self.num_data["numControlData"]):
                row_vals = []
                for col in range(self.num_data["numColumnsMessageIDs"]):
                    off = msg_id_offset + 4*(row*self.num_data["numColumnsMessageIDs"]+col)
                    val = struct.unpack(endian+'I', data[off:off+4])[0]
                    row_vals.append({"value": val, "offset": off})
                self.message_ids.append(row_vals)

        # ControlInfo Names
        self.control_info["filename"] = read_null_terminated_string(data, self.name_table_offset + 4 + self.control_info["filenameOffset"])
        self.control_info["className"] = read_null_terminated_string(data, self.name_table_offset + 4 + self.control_info["classNameOffset"])
        self.control_info["layoutName"] = read_null_terminated_string(data, self.name_table_offset + 4 + self.control_info["layoutNameOffset"])

    # --- Populate Tree ---
    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.obj_refs.clear()
        self.next_obj_id = 0

        # Header
        header_node = self.tree.insert("", "end", text="BCTRHeader")
        for k,v in self.header.items():
            self.tree.insert(header_node, "end", text=f"{k}: {v}", values=("header", k))

        # ControlInfo
        ci_node = self.tree.insert("", "end", text="BCTRControlInfo")
        for k,v in self.control_info.items():
            if k.endswith("Offset"):
                continue
            self.tree.insert(ci_node, "end", text=f"{k}: {v}", values=("control_info", k))

        # NumData
        num_node = self.tree.insert("", "end", text="BCTRNumData")
        for k,v in self.num_data.items():
            self.tree.insert(num_node, "end", text=f"{k}: {v}", values=("num_data", k))

        # MessageDataResources
        md_node = self.tree.insert("", "end", text=f"MessageDataResources ({len(self.message_data_resources)} entries)")
        for i, entry in enumerate(self.message_data_resources):
            obj_id = f"obj_{self.next_obj_id}"; self.next_obj_id += 1
            self.obj_refs[obj_id] = entry
            self.tree.insert(md_node, "end", text=f"{entry['name']}", values=("message_data_resource", obj_id))

        # ControlData
        cd_node = self.tree.insert("", "end", text=f"ControlData ({len(self.control_data_entries)} entries)")
        for i, entry in enumerate(self.control_data_entries):
            # main node
            obj_id_main = f"obj_{self.next_obj_id}"; self.next_obj_id += 1
            self.obj_refs[obj_id_main] = entry
            main_id = self.tree.insert(cd_node, "end", text=f"{entry['name']}", values=("control_data_entry", obj_id_main))
            # subfields
            for field in ["name", "drawOnBottomScreen", "position"]:
                obj_id_sub = f"obj_{self.next_obj_id}"; self.next_obj_id += 1
                self.obj_refs[obj_id_sub] = entry
                self.tree.insert(main_id, "end", text=f"{field}: {entry[field]}", values=("control_data_field", field, obj_id_sub))

        # MessageIDs
        msg_node = self.tree.insert("", "end", text="MessageIDs")
        for i,row in enumerate(self.message_ids):
            row_text = ", ".join([str(v["value"]) for v in row])
            self.tree.insert(msg_node, "end", text=f"Row {i}: {row_text}", values=("message_ids_row", i))

    # --- Editing ---
    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item)["values"]
        if not values:
            return

        section_type = values[0]

        # --- NumData ---
        if section_type == "num_data":
            field = values[1]
            initial = self.num_data[field]
            new_val = simpledialog.askinteger("Edit Value", f"Enter new value for {field}", initialvalue=initial)
            if new_val is not None:
                self.num_data[field] = new_val
                offset = 16 + list(self.num_data.keys()).index(field)*2
                self.data[offset:offset+2] = struct.pack('<H', new_val)
                self.tree.item(item, text=f"{field}: {new_val}")

        # --- ControlInfo ---
        elif section_type == "control_info":
            field = values[1]
            initial = self.control_info[field]
            new_val = simpledialog.askstring("Edit ControlInfo", f"Enter new value for {field}", initialvalue=initial)
            if new_val:
                offset_field = self.control_info[field+"Offset"]
                write_null_terminated_string(self.data, self.name_table_offset + 4 + offset_field, new_val)
                self.control_info[field] = new_val
                self.tree.item(item, text=f"{field}: {new_val}")

        # --- ControlData Subfields ---
        elif section_type == "control_data_field":
            field_name = values[1]
            obj_id = values[2]
            entry = self.obj_refs[obj_id]

            if field_name == "name":
                new_name = simpledialog.askstring("Edit Name", "Enter new name:", initialvalue=entry["name"])
                if new_name:
                    write_null_terminated_string(self.data, self.name_table_offset + 4 + entry["nameOffset"], new_name)
                    entry["name"] = new_name
                    self.tree.item(item, text=f"name: {new_name}")
                    parent_id = self.tree.parent(item)
                    self.tree.item(parent_id, text=new_name)

            elif field_name == "drawOnBottomScreen":
                new_val = simpledialog.askinteger("Edit drawOnBottomScreen", "0 or 1", initialvalue=entry["drawOnBottomScreen"])
                if new_val in [0,1]:
                    entry["drawOnBottomScreen"] = new_val
                    offset = entry["offset_in_file"] + 2
                    self.data[offset:offset+2] = struct.pack('<H', new_val)
                    self.tree.item(item, text=f"drawOnBottomScreen: {new_val}")

            elif field_name == "position":
                x = simpledialog.askfloat("Position X", "X:", initialvalue=entry["position"][0])
                y = simpledialog.askfloat("Position Y", "Y:", initialvalue=entry["position"][1])
                z = simpledialog.askfloat("Position Z", "Z:", initialvalue=entry["position"][2])
                if None not in (x,y,z):
                    entry["position"] = (x,y,z)
                    offset = entry["offset_in_file"] + 4
                    self.data[offset:offset+12] = struct.pack('<3f', x, y, z)
                    self.tree.item(item, text=f"position: ({x:.5f}, {y:.5f}, {z:.5f})")

        # --- ControlData main node ---
        elif section_type == "control_data_entry":
            obj_id = values[1]
            entry = self.obj_refs[obj_id]
            # edit main node: rename
            new_name = simpledialog.askstring("Edit ControlData Entry", "Enter new main name:", initialvalue=entry["name"])
            if new_name:
                write_null_terminated_string(self.data, self.name_table_offset + 4 + entry["nameOffset"], new_name)
                entry["name"] = new_name
                self.tree.item(item, text=new_name)
                # also update subfields
                for child in self.tree.get_children(item):
                    text = self.tree.item(child, "text")
                    if text.startswith("name:"):
                        self.tree.item(child, text=f"name: {new_name}")

        # --- MessageDataResources ---
        elif section_type == "message_data_resource":
            obj_id = values[1]
            entry = self.obj_refs[obj_id]
            new_name = simpledialog.askstring("Edit MessageDataResource", "Enter new MSBT filename:", initialvalue=entry["name"])
            if new_name:
                write_null_terminated_string(self.data, self.name_table_offset + 4 + entry["nameOffset"], new_name)
                entry["name"] = new_name
                self.tree.item(item, text=f"{new_name}")

        # --- MessageIDs ---
        elif section_type == "message_ids_row":
            row_idx = values[1]
            row_vals = self.message_ids[row_idx]
            new_vals = []
            for i, v in enumerate(row_vals):
                val = simpledialog.askinteger(f"MessageIDs Row {row_idx}", f"Column {i} value:", initialvalue=v["value"])
                if val is None:
                    val = v["value"]
                v["value"] = val
                self.data[v["offset"]:v["offset"]+4] = struct.pack('<I', val)
                new_vals.append(val)
            row_text = ", ".join([str(v) for v in new_vals])
            self.tree.item(item, text=f"Row {row_idx}: {row_text}")

    def run(self):
        self.root.mainloop()


# --- Run App ---
if __name__ == "__main__":
    viewer = BCTRViewer()
    viewer.run()

