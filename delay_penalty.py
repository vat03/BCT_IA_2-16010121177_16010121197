import time
from hashlib import sha256

class Block:
    def __init__(self, index, previous_hash, timestamp, data, miner, difficulty):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.miner = miner
        self.difficulty = difficulty
        self.nonce = 0  # Initialize nonce
        self.hash = self.mine_block()  # Mine block to get hash

    def calculate_hash(self):
        block_header = f'{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.miner}{self.difficulty}{self.nonce}'
        return sha256(block_header.encode()).hexdigest()

    def mine_block(self):
        while True:
            hash_val = self.calculate_hash()
            if hash_val[:self.difficulty] == '0' * self.difficulty:
                return hash_val  # Return hash when mined successfully
            self.nonce += 1  # Increment nonce to find valid hash

class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty  # Initialize the difficulty attribute
        self.chain = [self.create_genesis_block()]
        self.miner_penalties = {}    # Store penalties for miners (points)
        self.miner_redflags = {}     # Track red flags for miners
        self.block_delay = {}        # Track mining time for miners
        self.block_reward = 1        # Fixed reward for successfully mining a block
        self.grace_period = 10       # 10 seconds delay is acceptable
        self.ban_threshold = 3       # Threshold for red flags to ban miners

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block", "System", self.difficulty)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, new_block, current_delay):
        # Only add the block if it passes validation
        if self.validate_block(new_block, current_delay):
            self.chain.append(new_block)
            # Check if the miner should be rewarded or only penalized
            if current_delay <= self.grace_period:  # Miner only gets reward if delay is within acceptable limit
                self.give_reward(new_block.miner)
            else:
                print(f"\033[93mMiner {new_block.miner} delayed, no rewards for this block.\033[0m")
            print(f"\n\u2705 Block {new_block.index} successfully mined by {new_block.miner} and added to the chain.\n")
        else:
            print(f"\u274C Block by {new_block.miner} rejected due to penalties or ban.\n")

    def validate_block(self, block, current_delay):
        # Check if delay exceeds the grace period (10 seconds)
        if current_delay > self.grace_period:
            penalty_points = -1  # Fixed penalty points for delay
            self.apply_penalty(block.miner, penalty_points, current_delay)
        
        # Check if the miner is banned
        if block.miner in self.miner_redflags and self.miner_redflags[block.miner] >= self.ban_threshold:
            print(f"\n\u26A0 Miner {block.miner} is \033[91mbanned\033[0m from mining due to excessive red flags!\n")
            return False

        return block.hash[:self.difficulty] == '0' * self.difficulty

    def apply_penalty(self, miner, penalty_points, delay):
        # Apply penalty points and assign red flags based on delay
        if miner not in self.miner_penalties:
            self.miner_penalties[miner] = penalty_points
        else:
            self.miner_penalties[miner] += penalty_points

        # Assign red flag for delay
        if miner not in self.miner_redflags:
            self.miner_redflags[miner] = 1
        else:
            self.miner_redflags[miner] += 1

        print(f"\u26A0 Penalty applied to miner \033[93m{miner}\033[0m for a delay of \033[91m{delay:.2f} seconds!\033[0m")
        print(f"Miner {miner} now has \033[91m{self.miner_penalties[miner]} points\033[0m and \033[91m{self.miner_redflags[miner]} red flags\033[0m.\n")

    def give_reward(self, miner):
        # Give the miner a fixed reward for successfully mining a block
        reward_for_block = self.block_reward

        if miner not in self.miner_penalties:
            self.miner_penalties[miner] = reward_for_block
        else:
            self.miner_penalties[miner] += reward_for_block

        print(f"\033[92mMiner {miner} awarded {reward_for_block} points for mining a block.\033[0m")

    def mine_new_block(self, data, miner, delay_seconds=0):
        previous_block = self.get_last_block()
        new_block = Block(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            timestamp=time.time(),
            data=data,
            miner=miner,
            difficulty=self.difficulty
        )

        # Simulate delay in broadcasting the block
        time.sleep(delay_seconds)

        # Here, call add_block directly to ensure validate_block is called only once
        self.add_block(new_block, delay_seconds)

# Example blockchain simulation with user input
blockchain = Blockchain(difficulty=3)

def user_input_block():
    print("\033[94m--- Blockchain Mining Simulation ---\033[0m\n")
    while True:
        # Get miner and block details from user input
        miner = input("\033[95mEnter the miner's name (or type 'exit' to finish): \033[0m")
        if miner.lower() == 'exit':
            break
        data = input("\033[95mEnter the block data: \033[0m")
        delay = int(input("\033[95mEnter delay in broadcasting the block (in seconds): \033[0m"))

        # Mine and add block based on user input
        blockchain.mine_new_block(data, miner, delay)

# Call function to accept user input for blocks
user_input_block()

# Display miner penalties and red flags after mining process
print("\n\033[94m--- Miner penalties and red flags summary ---\033[0m")
for miner, penalty in blockchain.miner_penalties.items():
    redflags = blockchain.miner_redflags.get(miner, 0)
    print(f"\033[95m{miner}:\033[0m {penalty} points, {redflags} red flags")
