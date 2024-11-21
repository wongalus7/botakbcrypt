import sys
import os
import platform
import multiprocessing
from passlib.hash import bcrypt
from colored import fg, attr

white = attr("bold") + fg("white")
green = attr("bold") + fg("green")
error = fg("#FF0000")
spin_chars = ["|", "/", "-", "\\"]

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def banner():
    clear_screen()
    print(green + """
 __   __  ___            __   __   __       __  ___ 
|__) /  \  |   /\  |__/ |__) /  ` |__) \ / |__)  |  
|__) \__/  |  /~~\ |  \ |__) \__, |  \  |  |     |  
      [ Mass Crack Bcrypt Hash Password ]
""" + attr("reset"))

def generate_custom_wordlist(base_word):
    variants = []
    suffixes = ["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12", "22", "23", "33", "34", "44", "45", "55", "56", "66", "67", "77", "78", "88", "89", "90", "99", "111", "123", "222", "234", "333", "345", "444", "456", "555", "567", "666", "678", "777", "789", "888", "890", "999", "1111", "1234", "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2222", "2345", "3333", "3456", "4444", "4567", "5555", "5678", "6666", "6789", "7777", "7890", "8888", "9999", "11111", "12345", "22222", "23456", "33333", "34567", "44444", "45678", "55555", "56789", "66666", "67890", "77777", "88888", "99999", "111111", "123456", "222222", "234567", "333333", "345678", "444444", "456789", "555555", "567890", "666666", "777777", "888888", "999999", "1111111", "1234567", "2222222", "2345678", "3333333", "3456789", "4444444", "4567890", "5555555", "6666666", "7777777", "8888888", "9999999", "11111111", "12345678", "22222222", "23456789", "33333333", "34567890", "44444444", "55555555", "66666666", "77777777", "88888888", "99999999", "111111111", "123456789", "222222222", "234567890", "333333333", "444444444", "555555555", "666666666", "777777777", "888888888", "999999999", "1111111111", "1234567890", "2222222222", "3333333333", "00", "000", "0000", "00000", "000000", "0000000", "00000000", "000000000", "0000000000", "4444444444", "5555555555", "6666666666", "7777777777", "8888888888", "9999999999", "09", "098", "0987", "09876", "098765", "0987654", "09876543", "098765432", "0987654321", "01"]
    symbols = ["", "!", "@", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~"]
    for symbol in symbols:
        for suffix in suffixes:
            variants.append(f"{base_word}{symbol}{suffix}")
    return variants

def crack_bcrypt(wordlist, custom_wordlist, hash_to_crack, result_dict, hash_index):
    try:
        combined_wordlist = custom_wordlist[:]
        with open(wordlist, "r", encoding="cp437") as text_file:
            combined_wordlist.extend(text_file.read().splitlines())

        total_words = len(combined_wordlist)
        for index, word in enumerate(combined_wordlist):
            spinner = spin_chars[index % len(spin_chars)]
            sys.stdout.write(f"\r{white}{hash_to_crack} {green}{spinner} {white}[ Bruteforce: {index + 1}{green}/{white}{total_words} ]{attr('reset')}")
            sys.stdout.flush()

            if bcrypt.verify(word.strip(), hash_to_crack):
                result_dict[hash_index] = word.strip()
                print(f"\n{green}{hash_to_crack}: Password '{word.strip()}' {attr('reset')}")
                return

        result_dict[hash_index] = None
    except Exception as e:
        sys.stdout.write(f"\n{error}ERROR! {str(e)}{attr('reset')}\n")

def main():
    try:
        banner()
        hashes = input(f"{green}Bcrypt Hashes (bcrypt1|bcrypt2|bcrypt3): {attr('reset')}").strip().split('|')
        base_word = input(f"{green}Enter base word for custom wordlist (default: admin): {attr('reset')}").strip() or "admin"
        wordlist = input(f"{green}Wordlist (default: wordy.txt): {attr('reset')}").strip() or "wordy.txt"

        # Generate custom wordlist
        custom_wordlist = generate_custom_wordlist(base_word)

        manager = multiprocessing.Manager()
        result_dict = manager.dict()

        jobs = []
        for idx, hash_to_crack in enumerate(hashes):
            hash_to_crack = hash_to_crack.strip()
            if hash_to_crack:
                process = multiprocessing.Process(target=crack_bcrypt, args=(wordlist, custom_wordlist, hash_to_crack, result_dict, idx))
                jobs.append(process)
                process.start()

        for job in jobs:
            job.join()

        print("\n\nResults:")
        for idx, hash_to_crack in enumerate(hashes):
            result = result_dict.get(idx)
            if result:
                print(f"{green}{hash_to_crack}: Password '{result}'{attr('reset')}")
            else:
                print(f"{error}{hash_to_crack}: Password not found.{attr('reset')}")

    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
