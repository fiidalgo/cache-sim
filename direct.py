#!/usr/bin/env python3

from mainmem import Memory
import math

class DirectMappedCache(dict):
    '''
    Implements a direct-mapped cache with a specified number of sets (`num_sets`).
    Each memory block is mapped to a specific cache location using a hash function based on the memory address.
    '''

    def __init__(self, num_sets):
        # Initialize counters for cache operations
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0

        # Set the number of sets in the cache
        self.num_sets = num_sets
        
        # Create an instance of the main memory
        self.mm = Memory()
        
        # Initialize the cache structure: a list of cache lines
        self.cache = [{'data': None, 'dirty': False, 'valid': False} for _ in range(num_sets)]

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
    
    def base_addr_to_dmc_index(self, base_addr):
        '''
        Calculate the index in the cache where the block should be mapped.
        The index is determined by taking the block address modulo the number of sets.
        '''
        return base_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE % self.num_sets
    
    def store_word(self, w_addr, w_data):
        # Calculate the cache index and tag from the write address
        index = self.base_addr_to_dmc_index(w_addr)
        tag = w_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        
        # Calculate the offset within the block where the word should be stored
        block_offset = (w_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE

        # Access the cache line at the calculated index
        cache_line = self.cache[index]
        self.cache_write_queries += 1

        if cache_line['valid'] and cache_line['tag'] == tag:
            # If the block is already in the cache and valid, update the word and mark the line as dirty
            cache_line['data'][block_offset] = w_data
            cache_line['dirty'] = True
        else:
            # If the block is not in the cache, or the tags don't match, handle the cache miss
            if cache_line['valid'] and cache_line['dirty']:
                # Write the dirty block back to main memory before replacing it
                self.mm.mm_write(cache_line['tag'] * self.mm.MAIN_MEMORY_BLOCK_SIZE, cache_line['data'])
            
            # Load the new block from main memory, update the word, and set the cache line's metadata
            cache_line['data'] = self.mm.mm_read(tag * self.mm.MAIN_MEMORY_BLOCK_SIZE)
            cache_line['data'][block_offset] = w_data
            cache_line['tag'] = tag
            cache_line['valid'] = True
            cache_line['dirty'] = True
            
            # Count the cache miss
            self.cache_write_misses += 1

    def load_word(self, r_addr):
        # Calculate the cache index and tag from the read address
        index = self.base_addr_to_dmc_index(r_addr)
        tag = r_addr // self.mm.MAIN_MEMORY_BLOCK_SIZE
        
        # Calculate the offset within the block where the word is located
        block_offset = (r_addr % self.mm.MAIN_MEMORY_BLOCK_SIZE) // self.mm.MAIN_MEMORY_WORD_SIZE

        # Access the cache line at the calculated index
        cache_line = self.cache[index]
        self.cache_read_queries += 1
        
        if cache_line['valid'] and cache_line['tag'] == tag:
            # If the block is already in the cache and valid, return the requested word
            return cache_line['data'][block_offset]
        else:
            # If the block is not in the cache, or the tags don't match, handle the cache miss
            if cache_line['valid'] and cache_line['dirty']:
                # Write the dirty block back to main memory before replacing it
                self.mm.mm_write(cache_line['tag'] * self.mm.MAIN_MEMORY_BLOCK_SIZE, cache_line['data'])
            
            # Load the new block from main memory, update the cache line's metadata, and return the requested word
            cache_line['data'] = self.mm.mm_read(tag * self.mm.MAIN_MEMORY_BLOCK_SIZE)
            cache_line['tag'] = tag
            cache_line['valid'] = True
            cache_line['dirty'] = False
            
            # Count the cache miss
            self.cache_read_misses += 1
            
            return cache_line['data'][block_offset]
