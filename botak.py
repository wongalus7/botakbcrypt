import sys
import time
import multiprocessing
import os
from passlib.hash import bcrypt
from colored import fg, attr

# Color definitions
white = attr("bold") + fg("white")
green = attr("bold") + fg("green")
error = fg("#FF0000")

# Spin characters for rotation effect
spin_chars = ["|", "/", "-", "\\"]

def banner():
    os.system('clear')
    print(green + """
 __   __  ___            __   __   __       __  ___ 
|__) /  \  |   /\  |__/ |__) /  ` |__) \ / |__)  |  
|__) \__/  |  /~~\ |  \ |__) \__, |  \  |  |     |  
      [ Mass Crack Bcrypt Hash Password ]
""" + attr("reset"))

def crack_bcrypt(wordlist: str, hash_to_crack: str, result_dict, hash_index) -> None:
    try:
        with open(wordlist, "r", encoding="cp437") as text_file:
            words = text_file.read().splitlines()
    except FileNotFoundError:
        print(f"{error}ERROR! Wordlist file is invalid!")
        sys.exit(1)
    except Exception as err:
        print(f"{error}ERROR! {err}")
        sys.exit(1)

    length = len(words)
    for index, word in enumerate(words):
        spinner = spin_chars[index % len(spin_chars)]
        
        # Display current line number out of total lines in wordlist
        sys.stdout.write(f"\r{white}{hash_to_crack} {green}{spinner} {white}Attempting word {index + 1} of {length}")
        sys.stdout.flush()
        time.sleep(0.01)
        
        if bcrypt.verify(word, hash_to_crack):
            result_dict[hash_index] = word
            sys.stdout.write(f"\r\n{green}{hash_to_crack}: Password '{word}' {attr('reset')}")
            return

    result_dict[hash_index] = None

def main():
    banner()
    
    hashes = input(f"{green}Bcrypt Hashes (bcrypt1|bcrypt2|bcrypt3): {attr('reset')}").strip().split('|')
    if not hashes or all(not h.strip() for h in hashes):
        print(f"{error}Error: No hashes provided.")
        sys.exit(1)
    wordlist = input(f"{green}Wordlist (default: wordy.txt): {attr('reset')}").strip()
    if not wordlist:
        wordlist = "wordy.txt"

    manager = multiprocessing.Manager()
    result_dict = manager.dict()

    jobs = []
    for idx, hash_to_crack in enumerate(hashes):
        hash_to_crack = hash_to_crack.strip()
        if not hash_to_crack:
            continue
        process = multiprocessing.Process(target=crack_bcrypt, args=(wordlist, hash_to_crack, result_dict, idx))
        jobs.append(process)
        process.start()

    for job in jobs:
        job.join()
    
    # Display results
    print("\n\nResults:")
    for idx, hash_to_crack in enumerate(hashes):
        hash_to_crack = hash_to_crack.strip()
        result = result_dict.get(idx)
        if result:
            print(f"{green}{hash_to_crack}: Password '{result}'{attr('reset')}")
        else:
            print(f"{error}{hash_to_crack}: Password not found.{attr('reset')}")

if __name__ == "__main__":
    main()
