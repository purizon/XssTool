# -*- coding: utf-8 -*-
import subprocess
import re
import random
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import time

# Start measuring time
start_time = time.time()

print("[\033[94mINF\033[0m] XSSmap v1.0.0 (\033[92mlatest\033[0m)")


#-------------------KATANA FUNCTION--------------------------------

# Define function to run katana
def run_katana(url):
    print("[\033[94mINF\033[0m] Starting Url crawling with katana ...")
    command = ["katana", "-u", url]
    try:
        with open("urls.txt", "w") as output_file:
            subprocess.check_call(command, stderr=subprocess.STDOUT, stdout=output_file)
        print("[\033[94mINF\033[0m] urls saved to urls.txt")

        
        # Starting Url cleaning
        print("[\033[94mINF\033[0m] Starting Url cleaning ...")
        with open("urls.txt", "r") as file:
            lines = file.readlines()
        with open("urls.txt", "w") as file:
            for line in lines:
                if line.startswith("http"):
                    file.write(line)
        print("[\033[94mINF\033[0m] Filtered URLs saved to urls.txt")

        

    except subprocess.CalledProcessError as e:
        print("Error:", e)

#-------------------END KATANA--------------------------------


#-------------------GAU FUNCTION--------------------------------
# Define function to run gau
def run_gau(url):
    print("[\033[94mINF\033[0m] Starting Url crawling with gau ...")
    command = ["gau", url]
    try:
        with open("gauurls.txt", "w") as output_file:
            subprocess.check_call(command, stderr=subprocess.STDOUT, stdout=output_file)
        print("[\033[94mINF\033[0m] gau urls saved to gauurls.txt")
    except subprocess.CalledProcessError as e:
        print("Error:", e)


#------------------END GAU--------------------------------


#-------------------WAYBACKURL FUNCTION--------------------------------
# Define function to run waybackurls
def run_waybackurls(url):
    print("[\033[94mINF\033[0m] Starting Url crawling with waybackurls ...")
    command = ["waybackurls", url]
    try:
        with open("wayurls.txt", "w") as output_file:
            subprocess.check_call(command, stderr=subprocess.STDOUT, stdout=output_file)
        print("[\033[94mINF\033[0m] waybackurls saved to wayurls.txt")
    except subprocess.CalledProcessError as e:
        print("Error:", e)


#-------------------END WAYBACKURL-----------------------------

# URL to crawl
url = "https://www.emi.ac.ma/"

#-------------------MULTITHREADING THE TOOLS---------------

# Create threads for each crawler
katana_thread = threading.Thread(target=run_katana, args=(url,))
gau_thread = threading.Thread(target=run_gau, args=(url,))
waybackurls_thread = threading.Thread(target=run_waybackurls, args=(url,))

# Start all threads
katana_thread.start()
gau_thread.start()
waybackurls_thread.start()

# Wait for all threads to complete
katana_thread.join()
gau_thread.join()
waybackurls_thread.join()

#--------------------END MULTITHREADING TOOLS----------------

# Calculate merged elapsed time
end_time = time.time()
elapsed_time1 = end_time - start_time

# Print the elapsed time
print(f"[INFO] Elapsed time: {elapsed_time1:.2f} seconds")


#--------------------ALIVE FUNCTION------------------------

def alive_url(file_name):
    try:
        command=["httpx-toolkit","-status-code","-list",file_name,"-mc","200,302","-t" ,"100" ,"-rl" ,"300" ,"-timeout" ,"3" ,"-retries" ,"1" ,"-silent","|","cut" ,"-d" ,"' '" ,"-f" ,"1"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output_file_name = f"alive_{file_name}"
        with open(output_file_name, "w") as output_file:
            output_file.write(result.stdout)
        print(f"[\033[94mINF\033[0m] Alive URLs saved to {output_file_name}")
        return output_file_name
    except subprocess.CalledProcessError as e:
        print(f"Error processing {file_name}: {e}")
        return None


#---------------------END ALIVE FUNCTION----------------------


# After all threads complete, continue with cleaning and processing URLs


#-------------------MERGING FILES FUNCTION--------------------

# Merge files
def merge_files(file_list, output_file):
    with open(output_file, 'w') as output:
        for file_name in file_list:
            with open(file_name, 'r') as file:
                output.write(file.read().strip() + '\n')

#-------------------END MERGING FUNCTIONS----------------------



#----------EXECUTION OF ALIVE THREADED------------------------

files_to_merge = ['urls.txt', 'wayurls.txt', 'gauurls.txt']  # Liste des fichiers input pour alive function

#execution threaded de alive() 

alive_output_files = []
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(alive_url, file_name) for file_name in files_to_merge]

    for future in as_completed(futures):
        result = future.result()
        if result:
            alive_output_files.append(result)
    
#---------------END OF EXECUTION OF ALIVE THREADED-------------


#---------------MERGING OUTPUT OF ALIVE ---------------------

output_file = 'merged_output.txt'  # Nom du fichier de sortie
merge_files(alive_output_files, output_file)

print("[\033[94mINF\033[0m] Urls successfully merged : merged_output.txt")

#---------------END OF MERGING EXECUTION -------------------------------


#---------------------EXTRACTING VALID URLS REGEX  -------------

    # Extract valid URLs
def extract_urls_from_file(file_name):
    urls = []
    with open(file_name, 'r') as file:
        for line in file:
            url_match = re.search(r'(https?://\S+)', line)
            if url_match:
                urls.append(url_match.group(1))
    return urls

input_file = "merged_output.txt"  
print("[\033[94mINF\033[0m] Starting extracting valid urls ...")
urls = extract_urls_from_file(input_file)
print("[\033[94mINF\033[0m] Number of valid urls extracted", len(urls))


#-----------------------END OF EXTRACTING VALID URL REGEX --------------



#---------------------REMOVING FILES FROM URL FUNCTION------------------

# Cleaning URLs and removing duplicates
print("[\033[94mINF\033[0m] Starting cleaning urls and removing duplicates ...")
    
def remove_file_from_url(url):
    parts = url.split("/")
    if len(parts) > 3 and not any(parts[-1].endswith(extension) for extension in ['.php', '.html', '.aspx', '.json']):
        parts.pop()  # Remove the last part (file or directory)
    return "/".join(parts)
    

#----------------------END OF REMOVING FILES FROM URL FUNCTION-------------



#-------------------TRANSFORMING URL------------------------------------

def transform_url(url):
    parts = url.split("?")
    base_url = parts[0]
    if len(parts) > 1:
        query_params = parts[1]
        new_query_params = []
        for param in query_params.split("&"):
            key_value = param.split("=")
            if len(key_value) == 2:
                key, value = key_value
                if value != "random":
                    new_query_params.append(f"{key}=XSSMAP")
                else:
                    new_query_params.append(f"{key}={value}")
        if new_query_params:
            base_url += "?" + "&".join(new_query_params)
    return base_url


transformed_urls = [transform_url(url) for url in urls]


#if url doesn't contain param append XSSMAP to the path

urls_without_files = []
for url in transformed_urls:
    if "?" not in url:
        urls_without_files.append(remove_file_from_url(url) + "/XSSMAP")
    else:
        urls_without_files.append(url)
    
#----------------------END OF TRANSFORM URL -------------------------


#-----------------------REMOVING DUPLICATES ------------------

def remove_duplicates(list_urls):
    unique_list = list(set(list_urls))
    return unique_list

unique_list = remove_duplicates(urls_without_files)
    
#-----------------------END OF REMOVING DUPLICATES------------------
for i in unique_list:
    print(i)
    
# Generate random string
def generate_random_string():
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(8))
    return random_string
    
random_string = generate_random_string()
print("[\033[92m + \033[0m] Generating random string: \033[92m" + random_string + "\033[0m")



# Calculate elapsed time
end_time = time.time()
elapsed_time = end_time - start_time

# Print the elapsed time
print(f"[INFO] Elapsed time: {elapsed_time:.2f} seconds")
