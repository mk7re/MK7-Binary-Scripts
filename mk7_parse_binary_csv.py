#!/usr/bin/env python3
import struct
import csv
import sys

# Map command-line datatype to struct format and Python converter
DATA_TYPES = {
    "-int": ("<i", int),      # signed 32-bit
    "-f32": ("<f", float),    # 32-bit float
    "-vec3": ("<fff", float), # 3x 32-bit float vector
}


def bin_to_csv(input_file, output_file, dtype_key):
    """Convert binary file into human-readable CSV with chosen data type"""
    fmt, _ = DATA_TYPES[dtype_key]
    size_per_cell = struct.calcsize(fmt)

    with open(input_file, "rb") as f:
        # ---- HEADER ----
        header = f.read(12)
        ignore, num_rows, num_cols = struct.unpack("<III", header)
        print(f"[DEBUG] Ignored value: {ignore}")
        print(f"[DEBUG] Number of rows: {num_rows}")
        print(f"[DEBUG] Number of columns: {num_cols}")

        # ---- ROW NAMES ----
        row_names = []
        for _ in range(num_rows):
            raw = f.read(0x20)
            name = raw.decode("utf-8", errors="ignore").rstrip("\x00").strip()
            row_names.append(name)
        print(f"[DEBUG] Row names ({len(row_names)}): {row_names}")

        # ---- COLUMN NAMES ----
        col_names = []
        for _ in range(num_cols):
            raw = f.read(0x20)
            name = raw.decode("utf-8", errors="ignore").rstrip("\x00").strip()
            col_names.append(name)
        print(f"[DEBUG] Column names ({len(col_names)}): {col_names}")

        # ---- SKIP PADDING (dynamic based on number of columns) ----
        skip_size = num_cols * 2 * 4
        skipped = f.read(skip_size)
        print(f"[DEBUG] Skipped {len(skipped)} bytes (expected {skip_size})")

        # ---- TABLE DATA ----
        table = []
        for _ in range(num_rows):
            row = []
            for _ in range(num_cols):
                data = f.read(size_per_cell)
                if not data or len(data) != size_per_cell:
                    raise ValueError("Unexpected end of file at table values")

                if dtype_key == "-vec3":
                    x, y, z = struct.unpack(fmt, data)
                    row.extend([x, y, z])
                else:
                    val = struct.unpack(fmt, data)[0]
                    row.append(val)

            table.append(row)
        print(f"[DEBUG] Parsed table with {len(table)} rows")

    # ---- WRITE CSV ----
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if dtype_key == "-vec3":
            expanded_col_names = []
            for name in col_names:
                expanded_col_names.extend([
                    f"{name}.x",
                    f"{name}.y",
                    f"{name}.z"
                ])
            writer.writerow([""] + expanded_col_names)
        else:
            writer.writerow([""] + col_names)

        for name, row in zip(row_names, table):
            writer.writerow([name] + row)

    print(f"[INFO] CSV written to {output_file}")



def csv_to_bin(input_file, output_file, dtype_key):
    """Convert human-readable CSV into custom binary file with chosen data type"""
    fmt, caster = DATA_TYPES[dtype_key]
    size_per_cell = struct.calcsize(fmt)

    # ---- READ CSV ----
    with open(input_file, newline="") as csvfile:
        reader = list(csv.reader(csvfile))
        raw_col_names = reader[0][1:]
        rows = reader[1:]

    row_names = [r[0] for r in rows]

    if dtype_key == "-vec3":
        # Collapse COLUMN.x / COLUMN.y / COLUMN.z back into COLUMN
        col_names = []
        seen = set()

        for col in raw_col_names:
            base_name = col.rsplit('.', 1)[0]
            if base_name not in seen:
                seen.add(base_name)
                col_names.append(base_name)

        table = []
        for r in rows:
            values = [caster(v.replace(',', '.')) for v in r[1:]]

            if len(values) % 3 != 0:
                raise ValueError("Vec3 CSV data must contain groups of 3 values per column")

            vecs = []
            for i in range(0, len(values), 3):
                vecs.append((values[i], values[i + 1], values[i + 2]))

            table.append(vecs)
    else:
        col_names = raw_col_names
        table = [[caster(v.replace(',', '.')) for v in r[1:]] for r in rows]

    num_rows = len(row_names)
    num_cols = len(col_names)

    print(f"[DEBUG] Number of rows: {num_rows}")
    print(f"[DEBUG] Number of cols: {num_cols}")
    print(f"[DEBUG] Row names: {row_names}")
    print(f"[DEBUG] Column names: {col_names}")
    print(f"[DEBUG] Using datatype {dtype_key} ({fmt}), {size_per_cell} bytes per cell")

    with open(output_file, "wb") as f:
        # ---- HEADER ----
        f.write(struct.pack("<I", 0))  # ignored
        f.write(struct.pack("<I", num_rows))
        f.write(struct.pack("<I", num_cols))

        # ---- ROW NAMES ----
        for name in row_names:
            raw = name.encode("utf-8")[:0x20]
            raw = raw.ljust(0x20, b"\x00")
            f.write(raw)

        # ---- COLUMN NAMES ----
        for name in col_names:
            raw = name.encode("utf-8")[:0x20]
            raw = raw.ljust(0x20, b"\x00")
            f.write(raw)

        # ---- PADDING (dynamic based on number of columns) ----
        padding_size = num_cols * 2 * 4
        f.write(b"\x00" * padding_size)
        print(f"[DEBUG] Wrote {padding_size} bytes of padding")

        # ---- TABLE ----
        for row in table:
            for val in row:
                if dtype_key == "-vec3":
                    f.write(struct.pack(fmt, val[0], val[1], val[2]))
                else:
                    f.write(struct.pack(fmt, val))

    print(f"[INFO] Binary file written to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            f"Usage: {sys.argv[0]} "
            "<mode: bin2csv|csv2bin> "
            "<datatype: -int|-f32|-vec3> "
            "<input_file> <output_file>"
        )
        sys.exit(1)

    mode, dtype_key, infile, outfile = (
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4]
    )

    if dtype_key not in DATA_TYPES:
        print("Invalid datatype. Use -int, -f32, or -vec3.")
        sys.exit(1)

    if mode == "bin2csv":
        bin_to_csv(infile, outfile, dtype_key)
    elif mode == "csv2bin":
        csv_to_bin(infile, outfile, dtype_key)
    else:
        print("Invalid mode. Use 'bin2csv' or 'csv2bin'.")
        sys.exit(1)
