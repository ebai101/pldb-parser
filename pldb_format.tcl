# PluginDatabase template for Hex Fiend

big_endian

proc version_tag {} {
    variable major
    variable minor
    variable revision

    # reserved, major, minor, revision, reserved
    move 1
    set major [uint8]
    set minor [uint8]
    set revision [uint8]
    move -4

    entry "data version" [format "%d.%d.%d" $major $minor $revision] 5
    move 5
}

proc string {string_name} {
    variable string_size

    set string_size [uint32]
    ascii $string_size $string_name
}

proc pldv {} {
    variable pldv_size

    move 4
    set pldv_size [uint32]
    version_tag
    if {$pldv_size % 2 > 0} {
        move 1
    }
}

proc plck {} {
    # PLCK tag, size
    move 8
    version_tag
    string "filename"
    move 4
    hex 2 "weird tag 1"
    uint32
    hex 2 "weird tag 2"
    uint32 "enabled"
    set enabled [uint32 "crashed"]
    move 2
    if {[pos] % 2 > 0} {
        move 1
    }
    return $enabled
}

proc plpr {} {
    # FORM tag, size
    move 8
    version_tag
    move 1
    string "name"
    string "manufacturer"
    string "min version"
    string "maj version"
    uint32 "type"
    string "vst_id"
    move 2
    set num_categories [uint8]
    for {set n 0} {$n < $num_categories} {incr n} {
        string "category"
    }
    if {[pos] % 2 > 0} {
        move 1
    }
}

proc plugin {} {
    section "PLCK" {
        set crashed [plck]
    }
    if {$crashed != 2} {
        section "PLPR" {
            plpr
        }
    }
    if {[pos] % 2 > 0} {
        move 1
    }
}

#
#  begin main template
#

# initial FORM tag
move 4
uint32 "db size"

# PLDB tag
move 4
pldv

set i 0
while {![end]} {
    # FORM tag, size
    move 8
    set chunk_name [ascii 4]
    if {$chunk_name == "IGDB"} {
        break
    }
    
    section "Plugin $i" {
        plugin
    }
    incr i
}
