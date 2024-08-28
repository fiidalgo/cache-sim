#!/usr/bin/env python3

from mainmem import Memory
import math

class FullyAssociativeCache(list):
    '''
    Simulates a fully associative cache with a specified number of cache blocks (`num_ways`).
    Uses a Least-Recently Used (LRU) policy to evict cache blocks when necessary.
    '''

    def __init__(self, num_ways):
        # Initialize counters for cache operations
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0

        # Set the number of cache blocks (ways)
        self.num_ways = num_ways
        
        # Create an instance of the main memory
        self.mm = Memory()
        
        # Initialize the cache structure: a list of cache blocks
        self.cache = [{'data': None, 'tag': None, 'dirty': False, 'valid': False, 'last_used': 0} for _ in range(num_ways)]
        
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
        
    def find_least_recently_used(self):
        # Find and return the least recently used block in the cache
        return min(self.cache, key=lambda x: x['last_used'])

    def locate_block(self, tag):
        '''
        Searches for a cache block with the specified tag.
        Returns the block if found, otherwise returns None.
        '''
        for block in self.cache:
            if block['valid'] and block['tag'] == tag:
                return block
        return None

    def update_usage(self, block):
        # Update the access counter and set the block's last used time to the current counter value
        self.access_counter += 1
        block['last_used'] = self.access_counter

    def store_word(self, w_addr, w_data):
        # Calculate the tag and block offset from the write address
        tag = w_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        block_offset = (w_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE
        
        # Try to locate the block in the cache
        block = self.locate_block(tag)
        self.cache_write_queries += 1

        if block and block['valid']:
            # If the block is found and valid, update the word and mark it as dirty
            block['data'][block_offset] = w_data
            block['dirty'] = True
        else:
            # If the block is not found, find the least recently used block in the cache
            block = self.find_least_recently_used()
            
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
        self.update_usage(block)

    def load_word(self, r_addr) -> int:
        # Calculate the tag and block offset from the read address
        tag = r_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        block_offset = (r_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE
        
        # Try to locate the block in the cache
        block = self.locate_block(tag)
        self.cache_read_queries += 1

        if block and block['valid']:
            # If the block is found and valid, update its usage and return the requested word
            self.update_usage(block)
            return block['data'][block_offset]
        else:
            # If the block is not found, find the least recently used block in the cache
            block = self.find_least_recently_used()
            
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
            self.update_usage(block)
            return block['data'][block_offset]
