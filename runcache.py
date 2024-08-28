#!/usr/bin/env python3

import argparse
import re

from simple import SimpleCache
from direct import DirectMappedCache
from fully import FullyAssociativeCache
from setassoc import SetAssociativeCache

# Function to parse command-line arguments passed to the program
def parse_cli_args():

    parser = argparse.ArgumentParser()
    
    # Argument for specifying the number of sets in the cache
    parser.add_argument(
        '--num_sets',
        type=int,
        default=16,
        help='the number of sets per cache')
    
    # Argument for specifying the number of ways (associativity) in the cache
    parser.add_argument(
        '--num_ways',
        type=int,
        default=16,
        help='the number of ways per set')

    # Argument for specifying the test trace file to use
    parser.add_argument(
        '--testfile',
        type=str,
        default='tests/t1.test',
        # required=True,  # Uncomment if the testfile should be required
        help='the test trace file (with read/write addrs and vals) to run')

    # Argument for specifying the type of cache to simulate
    parser.add_argument(
        '--cachetype',
        choices=('simple', 'dmc', 'sac', 'fac'),
        default='simple',
        type=str.lower,
        help='the cache structure type (simple, DMC, SAC, or FAC)'
    )

    # Parse the arguments and return them as a namespace object
    return parser.parse_args()

# Class to run the cache simulation based on provided configuration
class CacheRunner():
    def __init__(self, structure, ways, sets, testfile):
        self.cache_type = structure  # Store the type of cache structure
        self.testfile = testfile  # Store the test file path
        self.hit_time = 1  # Set the default hit time for cache hits
        self.miss_penalty = 10  # Set the default miss penalty (for quantitative modeling)
        
        # Initialize the appropriate cache structure based on the cache type
        if (self.cache_type == "simple"):
            self.c = SimpleCache()  # Simple cache (no actual caching)
            self.descriptor = f"{self.cache_type} cache\n*******************************************"
        elif (self.cache_type == "dmc"):
            self.num_sets = sets  # Direct-mapped cache with the specified number of sets
            self.c = DirectMappedCache(self.num_sets)
            self.descriptor = f"{self.cache_type} cache with {self.num_sets} set(s)\n*******************************************"
        elif (self.cache_type == "fac"):
            self.num_ways = ways  # Fully associative cache with the specified number of ways
            self.c = FullyAssociativeCache(self.num_ways)
            self.descriptor = f"{self.cache_type} cache with {self.num_ways} way(s)\n*******************************************"
        elif (self.cache_type == "sac"):
            self.num_sets = sets  # Set-associative cache with the specified number of sets and ways
            self.num_ways = ways
            self.c = SetAssociativeCache(self.num_sets, self.num_ways)
            self.descriptor = f"{self.cache_type} cache with {self.num_sets} set(s) and {self.num_ways} way(s)\n*******************************************"

    # Method to run the cache simulation using the provided test file
    def run(self):
        with open(self.testfile, "r") as t:
            # Process each line in the test file
            while(line := t.readline()):
                # Handle write operations by matching the pattern "W <address> <data>"
                if matches := re.search(r"^W\s+(0x[0-9a-zA-Z]{4})\s+(-?[0-9]+)\s*$", line):
                    addr = int(matches.group(1), base=16)  # Convert address from hex to int
                    data = int(matches.group(2))  # Convert data to int
                    self.c.store_word(addr, data)  # Store the word in the cache
                    print(f"{self.cache_type}: Wrote to {'0x{:04x}'.format(addr)}: {data}\n")
                # Handle read operations by matching the pattern "R <address>"
                elif matches := re.search(r"^R\s+(0x[0-9a-zA-Z]{4})\s*$", line):
                    addr = int(matches.group(1), base=16)  # Convert address from hex to int
                    readval = self.c.load_word(addr)  # Load the word from the cache
                    print(f"{self.cache_type}: Read from {'0x{:04x}'.format(addr)} the value: {readval}\n")
                else:
                    print("Invalid test format")  # Print an error message for invalid format
        self.print_stats()  # Print the cache statistics after processing the test file

    # Method to print cache performance statistics
    def print_stats(self):
        print("\n\n*******************************************")
        write_hits      = self.c.cache_write_queries - self.c.cache_write_misses
        write_hit_rate  = write_hits/self.c.cache_write_queries * 100 if self.c.cache_write_queries else 0
        read_hits       = self.c.cache_read_queries - self.c.cache_read_misses
        read_hit_rate   = read_hits/self.c.cache_read_queries * 100 if self.c.cache_read_queries else 0
        total_hits      = write_hits + read_hits
        total_queries   = self.c.cache_write_queries + self.c.cache_read_queries
        total_hit_rate  = total_hits / total_queries * 100 if total_queries else 0
        queries         = self.c.cache_write_queries + self.c.cache_read_queries
        misses          = self.c.cache_write_misses + self.c.cache_read_misses
        amat = self.hit_time + (misses/queries)*self.miss_penalty if queries else 0
        
        # Print a summary of cache performance
        print(self.descriptor)
        print(f"Write Hit Rate:	    {'{:.2f}'.format(write_hit_rate)}% ({write_hits}/{self.c.cache_write_queries})")
        print(f"Read Hit Rate:	    {'{:.2f}'.format(read_hit_rate)}% ({read_hits}/{self.c.cache_read_queries})")
        print(f"Total Hit Rate:     {'{:.2f}'.format(total_hit_rate)}% ({total_hits}/{total_queries})")
        print(f"Writes to Main Memory:   {self.c.mm.write_queries}")
        print(f"Reads from Main Memory:  {self.c.mm.read_queries}")
        print(f"Avg. Memory Access Time: {'{:.2f}'.format(amat)} cycles")
        print("*******************************************")

# Main function to parse command-line arguments and run the cache simulation
def main():
    cli_args = parse_cli_args()  # Parse the command-line arguments
    CacheRunner(cli_args.cachetype, cli_args.num_ways, cli_args.num_sets, cli_args.testfile).run()  # Run the simulation

# Entry point of the script
if __name__ == '__main__':
    main()
