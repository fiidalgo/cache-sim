#!/usr/bin/env python3

class Memory(dict):
    '''
    Simulates main memory by reading from a memory initialization file (`mm_init.data`).
    The memory is represented as a dictionary where each key is an address and the value is a list of data (a memory block).
    Provides methods to read from and write to this simulated memory.
    '''

    def __init__(self):
        # Initialize memory configuration constants
        self.MAIN_MEMORY_SIZE            = 65536  # Total memory size in bytes
        self.MAIN_MEMORY_SIZE_LN         = 16     # Logarithm base 2 of memory size (16-bit addresses)
        self.MAIN_MEMORY_START_ADDR      = 0x0000 # Starting address of main memory
        self.MAIN_MEMORY_BLOCK_SIZE      = 32     # Block size in bytes
        self.MAIN_MEMORY_BLOCK_SIZE_LN   = 5      # Logarithm base 2 of block size (5 bits)
        self.MAIN_MEMORY_INIT_FILE       = "./mm_init.data"  # File to initialize memory contents
        self.MAIN_MEMORY_WORD_SIZE       = 4      # Size of a word in bytes (4 bytes for RISC-V)
        self.MAIN_MEMORY_WORDS_PER_BLOCK = self.MAIN_MEMORY_BLOCK_SIZE // self.MAIN_MEMORY_WORD_SIZE

        # Counters for read and write operations
        self.write_queries  = 0
        self.read_queries   = 0

        # Initialize the memory dictionary with the first block
        self[0] = []  

        # Load memory contents from the initialization file
        with open(self.MAIN_MEMORY_INIT_FILE, mode="rb") as mem_init:
            i = 0   # Index representing the block-aligned address in memory
            j = 0   # Index within a block (word index)
            while (byte := mem_init.read(4)):  # Read 4 bytes (1 word) at a time
                # Convert the read bytes into an integer and append to the current block
                self[i].append(int.from_bytes(byte, byteorder="little", signed=True))
                j += 1
                
                # If the block is full, move to the next block
                if j >= self.MAIN_MEMORY_WORDS_PER_BLOCK:
                    j = 0
                    i += self.MAIN_MEMORY_BLOCK_SIZE
                    self[i] = []  # Initialize the next block in memory

    # Method to read a block of memory from the specified address
    def mm_read(self, addr) -> list:
        if addr in self:
            self.read_queries += 1  # Increment the read operation counter
            print(f"MM:  Read {self.MAIN_MEMORY_BLOCK_SIZE} bytes at {'0x{:04x}'.format(addr)}")
            return self[addr]  # Return the block of memory as a list
        else:
            raise Exception("INVALID MAIN MEMORY ADDRESS")  # Raise an error if the address is invalid

    # Method to write a block of memory to the specified address
    def mm_write(self, addr, block):
        # Ensure that the block size matches the expected block size in words
        assert len(block) == self.MAIN_MEMORY_WORDS_PER_BLOCK, "MAINMEM ERROR: wrong sized block!"
        
        if addr in self:
            self.write_queries += 1  # Increment the write operation counter
            print(f"MM:  Wrote {self.MAIN_MEMORY_BLOCK_SIZE} bytes at {'0x{:04x}'.format(addr)}")
            self[addr] = block  # Write the block to the specified address
        else:
            raise Exception("INVALID MAIN MEMORY ADDRESS")  # Raise an error if the address is invalid
