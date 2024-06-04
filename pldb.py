import struct
from pprint import pprint
from chunk_reader import Chunk


infile = "/Users/ethan/Library/Application Support/Propellerhead Software/Reason/Caches/__PluginDatabase_v4-arm64.dat"
out_data = {"plugins": []}


def data_version(c):
    data = c.read(5)
    version = [
        int.from_bytes(n, byteorder="big") for n in struct.unpack(">x1c1c1cx", data)
    ]
    return f"{version[0]}.{version[1]}.{version[2]}"


def readstr(c):
    size = struct.unpack(">I", c.read(4))[0]
    string = struct.unpack(f">{size}s", c.read(size))[0].decode("utf-8")
    return string


def parse(f):
    outer_form = Chunk(f)
    out_data["db size"] = outer_form.getsize()

    outer_form.seek(4)
    pldv = Chunk(outer_form)
    out_data["data_version"] = data_version(pldv)
    outer_form.seek(pldv.tell() + 12)

    for x in range(988):
        try:
            c = Chunk(outer_form)
        except EOFError:
            break
        c.seek(4)
        plugin = {}

        plck = Chunk(c)
        plugin["plck"] = {}
        plugin["plck"]["data_version"] = data_version(plck)
        plugin["plck"]["filename"] = readstr(plck)
        plck.seek(4, whence=1)
        plugin["plck"]["unknown_tag_1"] = hex(struct.unpack(">H", plck.read(2))[0])
        plck.seek(4, whence=1)
        plugin["plck"]["unknown_tag_2"] = hex(struct.unpack(">H", plck.read(2))[0])
        plugin["plck"]["enabled"] = struct.unpack(">I", plck.read(4))[0]
        plugin["plck"]["enabled_offset"] = outer_form.tell() + 4
        plugin["plck"]["crashed"] = struct.unpack(">I", plck.read(4))[0]
        plck.skip()

        if plugin["plck"]["crashed"] == 2:
            continue
        plpr = Chunk(c)
        plugin["plpr"] = {}
        plugin["plpr"]["data_version"] = data_version(plpr)
        plpr.seek(1, whence=1)
        plugin["plpr"]["name"] = readstr(plpr)
        plugin["plpr"]["manufacturer"] = readstr(plpr)
        plugin["plpr"]["min_version"] = readstr(plpr)
        plugin["plpr"]["maj_version"] = readstr(plpr)
        plugin["plpr"]["type"] = struct.unpack(">I", plpr.read(4))[0]
        plugin["plpr"]["vst_id"] = readstr(plpr)
        plpr.seek(2, whence=1)
        plugin["plpr"]["categories"] = []
        num_categories = int.from_bytes(plpr.read(1), byteorder="big")
        for i in range(num_categories):
            plugin["plpr"]["categories"].append(readstr(plpr))
        plpr.skip()

        out_data["plugins"].append(plugin)

    return out_data


if __name__ == "__main__":
    with open(infile, "rb") as f:
        data = parse(f)
        pprint(data)
        # print("disabled plugins")
        # pprint(
        #     [x["plpr"]["name"] for x in data["plugins"] if x["plck"]["enabled"] != 3]
        # )
