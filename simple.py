#!/usr/bin/env python3

from mainmem import Memory
import math

class SimpleCache():
    '''
    A simple cache class that does not actually cache data.
    Instead, it always accesses the main memory directly.
    '''

    def __init__(self):
        # Initialize counters for cache operations and connect to main memory
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0
        self.mm = Memory()  
    
    def calculate_base_index(self, addr):
        # Ensure the memory address is aligned to a 4-byte boundary
        assert (addr % 4 == 0), "Misaligned Memory Address"
        
        # Calculate the base address of the block containing the word
        addr_offt = ((addr - self.mm.MAIN_MEMORY_START_ADDR) % self.mm.MAIN_MEMORY_BLOCK_SIZE)
        base = addr - addr_offt
        
        # Calculate the index within the block where the word is located
        index = math.floor(addr_offt / self.mm.MAIN_MEMORY_WORD_SIZE)
        
        # Return the base address of the block and the index of the word within that block
        return base, index

    def store_word(self, w_addr, w_data):
        # Calculate the block's base address and the index for the word within the block
        base_addr, index_in_block = self.calculate_base_index(w_addr)
        
        # Read the entire block from main memory
        block = self.mm.mm_read(base_addr)
        
        # Store the word in the correct position within the block
        block[index_in_block] = w_data
        
        # Write the updated block back to main memory
        self.mm.mm_write(base_addr, block)
        
        # Update write operation counters: count the write query and mark it as a miss
        self.cache_write_queries += 1
        self.cache_write_misses  += 1  # This always counts as a miss since there is no actual caching

    def load_word(self, r_addr) -> int:
        # Calculate the block's base address and the index for the word within the block
        base_addr, index_in_block = self.calculate_base_index(r_addr)
        
        # Read the block containing the requested word from main memory
        block = self.mm.mm_read(base_addr)
        
        # Retrieve the word from the block
        val = block[index_in_block]
        
        # Update read operation counters: count the read query and mark it as a miss
        self.cache_read_queries += 1
        self.cache_read_misses  += 1  # This always counts as a miss since there is no actual caching
        
        # Return the word that was loaded from memory
        return val
