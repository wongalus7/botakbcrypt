<?php
error_reporting(0);

# Function to clear the screen
function clear_screen() {
    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        system('cls');
    } else {
        system('clear');
    }
}

# Function to display a banner
function display_banner() {
    $green = "\033[1;32m";
    $white = "\033[1;37m";
    $reset = "\033[0m";

    echo $green . "
 __   __  ___            __   __   __       __  ___ 
|__) /  \  |   /\  |__/ |__) /  ` |__) \ / |__)  |  
|__) \__/  |  /~~\ |  \ |__) \__, |  \  |  |     |    
       [ Mass Bcrypt Hash Bruteforce Tool ]\n
" . $reset;
}

# Function to filter special characters from wordlist
function filter_special_characters($wordlist) {
    return array_filter($wordlist, function($word) {
        return preg_match('/^[a-zA-Z0-9]+$/', $word); # Only alphanumeric
    });
}

# Function to generate custom wordlist based on base word
function generate_custom_wordlist($base_word) {
    $variants = [];
    $suffixes = ["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12", "22", "23", "33", "34", "44", "45", "55", "56", "66", "67", "77", "78", "88", "89", "90", "99", "111", "123", "222", "234", "333", "345", "444", "456", "555", "567", "666", "678", "777", "789", "888", "890", "999", "1111", "1234", "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2222", "2345", "3333", "3456", "4444", "4567", "5555", "5678", "6666", "6789", "7777", "7890", "8888", "9999", "11111", "12345", "22222", "23456", "33333", "34567", "44444", "45678", "55555", "56789", "66666", "67890", "77777", "88888", "99999", "111111", "123456", "222222", "234567", "333333", "345678", "444444", "456789", "555555", "567890", "666666", "777777", "888888", "999999", "1111111", "1234567", "2222222", "2345678", "3333333", "3456789", "4444444", "4567890", "5555555", "6666666", "7777777", "8888888", "9999999", "11111111", "12345678", "22222222", "23456789", "33333333", "34567890", "44444444", "55555555", "66666666", "77777777", "88888888", "99999999", "111111111", "123456789", "222222222", "234567890", "333333333", "444444444", "555555555", "666666666", "777777777", "888888888", "999999999", "1111111111", "1234567890", "2222222222", "3333333333", "00", "000", "0000", "00000", "000000", "0000000", "00000000", "000000000", "0000000000", "4444444444", "5555555555", "6666666666", "7777777777", "8888888888", "9999999999", "09", "098", "0987", "09876", "098765", "0987654", "09876543", "098765432", "0987654321", "01"];
    $symbols = ["", "!", "@", "#", "$", "%", "&", "?", "~"];

    foreach ($symbols as $symbol) {
        foreach ($suffixes as $suffix) {
            $variants[] = "$base_word$symbol$suffix";
            $variants[] = "$base_word$suffix$symbol";
        }
    }
    return $variants;
}

# Function to process a batch of wordlist
function process_batch($hash, $wordlist_batch) {
    $total_words = count($wordlist_batch);
    $green = "\033[1;32m";
    $white = "\033[1;37m";
    $reset = "\033[0m";

    foreach ($wordlist_batch as $index => $password) {
        echo "\r{$green}[+] {$hash} {$white}[{$green}" . ($index + 1) . "/{$total_words}{$white}] {$green}| {$white}{$password}\033[K{$reset}";
        if (password_verify($password, $hash)) {
            echo "\r{$green}[+] Match Found: {$hash} -> {$password}\n{$reset}";
            return true;
        }
    }
    echo "\r{$white}[-] No match for: {$hash}\n{$reset}";
    return false;
}

# Main program
clear_screen();
display_banner();

# Prompt user for input
$hashes_input = readline("Bcrypt hash (bcrypt1|bcrypt2|bcrypt3): ");
$base_words_input = readline("Base word to generate powerful custom wordlist (admin|password): ");
$process_count_input = readline("Number of processes to use (5 or more.): \n");

if ($hashes_input && $base_words_input && is_numeric($process_count_input) && $process_count_input > 0) {
    $process_count = (int)$process_count_input;
    $hashes = explode('|', $hashes_input);
    $base_words = explode('|', $base_words_input);

    $wordlist = [];

    # Generate custom wordlist
    foreach ($base_words as $base_word) {
        $wordlist = array_merge($wordlist, generate_custom_wordlist(trim($base_word)));
    }

    # Include additional wordlist from file
    if (file_exists("wordy.txt")) {
        $file_wordlist = file("wordy.txt", FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $file_wordlist = filter_special_characters($file_wordlist);
        $wordlist = array_merge($wordlist, $file_wordlist);
    }

    # Deduplicate wordlist
    $wordlist = array_unique($wordlist);
    $total_words = count($wordlist);

    # Define batch size
    $batch_size = ceil($total_words / $process_count);

    # Fork processes
    $processes = [];
    foreach ($hashes as $hash) {
        $hash = trim($hash);
        for ($i = 0; $i < $total_words; $i += $batch_size) {
            $pid = pcntl_fork();
            if ($pid == -1) {
                die("Failed to fork\n");
            } elseif ($pid == 0) {
                $batch = array_slice($wordlist, $i, $batch_size);
                process_batch($hash, $batch);
                exit(0);
            } else {
                $processes[] = $pid;
            }
        }
    }

    # Wait for all processes to finish
    foreach ($processes as $pid) {
        pcntl_waitpid($pid, $status);
    }
} else {
    echo "Invalid input. Please provide valid hashes, base words, and process count.\n";
}
?>
