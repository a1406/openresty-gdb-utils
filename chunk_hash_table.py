import sys

import gdb
import gdbutils
import ngxlua
import re
import time

typ = gdbutils.typ
null = gdbutils.null
newval = gdbutils.newval
ptr2int = gdbutils.ptr2int
err = gdbutils.err
out = gdbutils.out
warn = gdbutils.warn

if sys.version_info[0] >= 3:  # Python 3K
    global xrange
    xrange = range

node_size = 24    
hash_set_detail_kDeletedHash = 4294967294
IndexScale = node_size & (0 - node_size) 

def get_end_node_ptr(nodes, scaledMask):
    return nodes.cast(typ("char *")) + scaledMask * (node_size / IndexScale) + node_size

def is_occupied(node):
    return node["hash"] < hash_set_detail_kDeletedHash;

def move_to_next_occupied_node(m_node, m_end):
    while m_node < m_end:
        if is_occupied(m_node):
            return m_node
        m_node = m_node + 1
        # {
        #     for (/**/; m_node < m_end; ++m_node)
        #     {
        #         if (m_node->is_occupied())
        #             break;
        #     }
        # }
            
class show_chunk_hash_table(gdb.Command):

    def __init__ (self):
        super (show_chunk_hash_table, self).__init__("show_chunk_hash_table", gdb.COMMAND_USER)

    def invoke (self, args, from_tty):
        argv = gdb.string_to_argv(args)
        show_data = False
        if len(argv) < 1:
            raise gdb.GdbError("1 argument expected!\nusage: show_chunk_hash_table table_address")
        if len(argv) > 1:
            if argv[1] == "*":
                show_data = True
        

        T = gdbutils.parse_ptr(argv[0], "World::ChunkHashTable*")
        m_nodes = T['m_nodes']
        m_scaledMask = T['m_scaledMask']

        end = get_end_node_ptr(m_nodes, m_scaledMask)
        begin = move_to_next_occupied_node(m_nodes, end)
        index = 0
        while (begin and begin < end):
            print("%s: %s" % (index, begin))
            if show_data:
                gdb.execute("p *(core::hash_set<core::pair<ChunkIndex const, ChunkViewerList*, false>, core::hash_pair<ChunkIndexHashCoder, ChunkIndex const, ChunkViewerList*>, core::equal_pair<std::equal_to<ChunkIndex>, ChunkIndex const, ChunkViewerList*> >::node *) %s" % begin)
            # p *(core::hash_set<core::pair<ChunkIndex const, ChunkViewerList*, false>, core::hash_pair<ChunkIndexHashCoder, ChunkIndex const, ChunkViewerList*>, core::equal_pair<std::equal_to<ChunkIndex>, ChunkIndex const, ChunkViewerList*> >::node *)0x7f9d3f1e13e0
            begin = move_to_next_occupied_node(begin + 1, end)
            index = index + 1

show_chunk_hash_table()
    
