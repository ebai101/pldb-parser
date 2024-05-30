import json
import socket
import struct
import pldb
from pprint import pprint


def recvall(sock):
    data = bytearray()
    while True:
        packet = sock.recv(4096)
        if not packet:
            break
        data.extend(packet)
        if b"\x00" in data:
            break
    return data


def command(s, cmd, wait=True):
    cmd = cmd + "\u0000"
    cmd = cmd.encode("utf-8")
    s.send(cmd)
    if wait:
        return json.loads(recvall(s).decode().replace("\u0000", ""))["data"]
    else:
        return


def get_uad_plugins(authorized=True):
    authorized_plugs = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 4710))
    command(s, "set /Sleep false", wait=False)
    plugin_count = len(command(s, "get /plugins")["children"])
    for p in range(plugin_count):
        plugin = command(s, f"get /plugins/{p}")
        if plugin["properties"]["Authorized"]["value"] == authorized:
            authorized_plugs.append(plugin["properties"]["Name"]["value"])
            authorized_plugs.append(plugin["properties"]["Name"]["value"] + "(m)")
    s.close()
    return authorized_plugs


def disable_plugin(file, offset):
    file.seek(offset)
    file.write(struct.pack(">I", 5))


infile = "pldb.dat"
plugins_to_disable = get_uad_plugins(authorized=False)

with open(infile, "r+b") as f:
    plugin_database_entries = [
        x for x in pldb.parse(f)["plugins"] if x["plpr"]["name"] in plugins_to_disable
    ]
    for entry in plugin_database_entries:
        print(f'Disabling {entry["plpr"]["name"]}')
        disable_plugin(f, entry["plck"]["enabled_offset"])
