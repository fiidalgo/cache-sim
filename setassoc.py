#!/usr/bin/env python3

from mainmem import Memory
import math

class SetAssociativeCache(dict):
    '''
    Implements a set-associative cache with a specified number of sets and ways.
    Uses a Least-Recently Used (LRU) policy for evicting cache blocks when necessary.
    '''

    def __init__(self, num_sets, num_ways):
        # Initialize counters for cache operations
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0

        # Set the number of sets and ways for the cache
        self.num_sets = num_sets
        self.num_ways = num_ways
        
        # Create an instance of the main memory
        self.mm = Memory()
        
        # Initialize the cache structure: a list of sets, each containing a list of blocks
        self.cache = [
            [{'data': None, 'tag': None, 'dirty': False, 'valid': False, 'last_used': 0} for _ in range(num_ways)]
            for _ in range(num_sets)
        ]
        
        # Access counter to track the usage of cache blocks for LRU policy
        self.access_counter = 0

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
    
    def calculate_set_index(self, addr):
        # Calculate the set index by taking the block address modulo the number of sets
        return (addr // self.mm.MAIN_MEMORY_BLOCK_SIZE) % self.num_sets

    def find_least_recently_used(self, set_index):
        # Find and return the least recently used block in the specified set
        return min(self.cache[set_index], key=lambda x: x['last_used'])

    def locate_block(self, set_index, tag):
        # Search for a block within the set that matches the given tag
        for block in self.cache[set_index]:
            if block['valid'] and block['tag'] == tag:
                return block
        # Return None if no matching block is found
        return None

    def update_usage(self, set_index, block):
        # Update the access counter and set the block's last used time to the current counter value
        self.access_counter += 1
        block['last_used'] = self.access_counter

    def store_word(self, w_addr, w_data):
        # Calculate the set index and tag from the write address
        set_index = self.calculate_set_index(w_addr)
        tag = w_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        
        # Calculate the offset within the block where the word should be stored
        block_offset = (w_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE
        
        # Try to locate the block in the cache
        block = self.locate_block(set_index, tag)
        self.cache_write_queries += 1

        if block and block['valid']:
            # If the block is found and valid, update the word and mark it as dirty
            block['data'][block_offset] = w_data
            block['dirty'] = True
        else:
            # If the block is not found, find the least recently used block in the set
            block = self.find_least_recently_used(set_index)
            
            # If the LRU block is dirty, write it back to main memory before replacing it
            if block['valid'] and block['dirty']:
                self.mm.mm_write(block['tag'] * self.mm.MAIN_MEMORY_BLOCK_SIZE, block['data'])
            
            # Load the new block from main memory, update the word, and set the block's metadata
            block['data'] = self.mm.mm_read(tag * self.mm.MAIN_MEMORY_BLOCK_SIZE)
            block['data'][block_offset] = w_data
            block['tag'] = tag
            block['valid'] = True
            block['dirty'] = True
            
            # Count the cache miss
            self.cache_write_misses += 1

        # Update the block's usage information for LRU management
        self.update_usage(set_index, block)

    def load_word(self, r_addr) -> int:
        # Calculate the set index and tag from the read address
        set_index = self.calculate_set_index(r_addr)
        tag = r_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        
        # Calculate the offset within the block where the word is located
        block_offset = (r_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE
        
        # Try to locate the block in the cache
        block = self.locate_block(set_index, tag)
        self.cache_read_queries += 1

        if block and block['valid']:
            # If the block is found and valid, update its usage and return the requested word
            self.update_usage(set_index, block)
            return block['data'][block_offset]
        else:
            # If the block is not found, find the least recently used block in the set
            block = self.find_least_recently_used(set_index)
            
            # If the LRU block is dirty, write it back to main memory before replacing it
            if block['valid'] and block['dirty']:
                self.mm.mm_write(block['tag'] * self.mm.MAIN_MEMORY_BLOCK_SIZE, block['data'])
            
            # Load the new block from main memory, update the block's metadata, and return the requested word
            block['data'] = self.mm.mm_read(tag * self.mm.MAIN_MEMORY_BLOCK_SIZE)
            block['tag'] = tag
            block['valid'] = True
            block['dirty'] = False
            
            # Count the cache miss
            self.cache_read_misses += 1
            
            # Update the block's usage information for LRU management
            self.update_usage(set_index, block)
            return block['data'][block_offset]
