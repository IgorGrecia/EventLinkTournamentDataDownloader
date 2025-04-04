import os
import pandas as pd
import os
import csv

SESSION_STORAGE_PATH = "session_storage.json"

username = "igorgrecia@gmail.com"
password = "9Woodlandacres>"
year = "2025"
base_url = "https://eventlink.wizards.com"

def list_folders_and_files():
    folders = {}
    # Get the current working directory
    current_directory = os.getcwd()
    
    # List all items in the current directory
    items = os.listdir(current_directory)
    
    # Iterate over each item
    for item in items:
        # Construct the full path
        item_path = os.path.join(current_directory, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path) and 'pycache' not in item_path:
            folders[item_path] = []
            
            # List all files in the folder
            files = os.listdir(item_path)
            for file in files:
                file_path = os.path.join(item_path, file)
                
                # Check if the item is a file (not a subfolder)
                if os.path.isfile(file_path):
                    folders[item_path].append(file)
    return folders

def write_to_sheets(folder_path, file_path, spreadsheet):
    df = pd.read_csv(file_path, delimiter="\t")
    data_to_append = [[str(item).strip().strip("\"") for item in row] for row in df.values.tolist()]
    # print(data_to_append)
    sheet_to_write = spreadsheet.worksheet("Rounds")

    if 'standings' in file_path.lower():
        sheet_to_write = spreadsheet.worksheet("Standings")    

    sheet_to_write.append_rows(data_to_append)

def save_storage(context):
	"""Save session storage to a file."""
	context.storage_state(path=SESSION_STORAGE_PATH)

def load_storage(browser):
	"""Load session storage from a file if it exists, otherwise return a new context."""
	if os.path.exists(SESSION_STORAGE_PATH):
		# print("Loaded Session")
		return browser.new_context(storage_state=SESSION_STORAGE_PATH, no_viewport=True), True
	else:
		# print("No session found, creating new session...")
		return browser.new_context(no_viewport=True), False

def extract_table_to_csv(input_string, output_file, round_number, folder_name, tr_format, tr_name, date):
	os.makedirs(folder_name, exist_ok=True)

	csv_filename = f"{folder_name}\\{output_file}.txt"

	lines = input_string.split('\n')
	input_type = ''
	
	# Find the starting point of the table
	start_index = next((i for i, line in enumerate(lines) if line.startswith("MESA")), None)
	input_type = 'mesa'
	if start_index is None:
		start_index = next((i for i, line in enumerate(lines) if line.startswith("CLASSIFICAÇÃO")), None)
		input_type = 'class'
		if start_index is None:
			return

	# print(start_index)
	stop_index = next((i for i, line in enumerate(lines) if line.startswith("©")), None)
	# print(stop_index)
	
	# Extract relevant lines and clean them up
	table_lines = [line.strip() for line in lines[start_index:stop_index] if line.strip()] if stop_index else [line.strip() for line in lines[start_index:] if line.strip()]
	
	# Write to CSV file
	if input_type == 'class':
		with open(csv_filename, 'w', encoding='utf-8', newline='') as outfile:
			writer = csv.writer(outfile, delimiter='\t')
			for line in table_lines:
				line = f"{line}\t{tr_format}\t{tr_name}\t{date}"
				writer.writerow(line.split('\t'))
	
	if input_type == 'mesa':
		with open(csv_filename, 'w', encoding='utf-8', newline='') as outfile:
			writer = csv.writer(outfile, delimiter='\t')
			for line in table_lines:
				writer.writerow(line.split('\t'))

		with open(csv_filename, "r", encoding="utf-8") as file:
			lines = file.readlines()
		matches = []

		line_count = len(lines)

		if 'Bye' in lines[len(lines)-1]:
			line_count -= 4

			player1 = lines[len(lines)-4].strip()

			matches.append([round_number, player1, "Win", "2", "0", "Loss", "Bye", tr_format, tr_name, date])

		i = 1  # Skip header row
		while i < line_count:
			player1 = lines[i + 1].strip()
			# score = lines[i + 2].strip()
			resultado = lines[i + 3].strip()
			player2 = lines[i + 4].strip()

			# print(player1)
			# print(player2)

			# Extracting player wins from resultado (format XX)
			player1_wins = int(resultado[0])
			player2_wins = int(resultado[1])

			# Determine result for each player
			if player1_wins > player2_wins:
				result1, result2 = "Win", "Loss"
			elif player1_wins < player2_wins:
				result1, result2 = "Loss", "Win"
			else:
				result1, result2 = "Draw", "Draw"

			# Store processed match
			matches.append([round_number, player1, result1, player1_wins, player2_wins, result2, player2, tr_format, tr_name, date])

			i += 6  # Move to next match set

		with open(csv_filename, 'w', encoding='utf-8', newline='') as outfile:
			writer = csv.writer(outfile, delimiter='\t')
			writer.writerow(["Round", "Player 1", "Result P1", "Player 1 Wins", "Player 2 Wins", "Result P2", "Player 2", "Format", "Tournament Name", "Date"])
			for line in matches:
				writer.writerow(line)

def get_weekly_tournament(tournament, page):
	try:
		close_button = "//*[@id=\"notification:eventlink_maintenance_feb_2025\"]/div[3]/button[2]"
		page.wait_for_selector(close_button, timeout=2000)
		page.click(close_button)
	except:
		pass
	
	date = f"{year}-{tournament[2]}-{tournament[1]}"
	# Find all elements with class "day-label-value"
	page.wait_for_selector(f"[class*=\"id-{date}\"]")
	element = page.query_selector(f"[class*=\"id-{date}\"]")
	try:
		page.wait_for_selector(f"text={tournament[0]}")
		weekly_pauper_button = element.query_selector(f"text={tournament[0]}")
		if weekly_pauper_button.is_visible():
			weekly_pauper_button.click()
			view_event_button = "//*[@id=\"event__actions-view\"]"
			page.wait_for_selector(view_event_button)
			page.click(view_event_button)

			try:
				got_it_button = "//*[@id=\"v-step-0e453292\"]/div[3]/button"
				page.wait_for_selector(got_it_button, timeout=2000)
				page.click(got_it_button)
			except:
				pass

			try:
				got_it_button = "//*[@id=\"v-step-5643f0e0\"]/div[3]/button"
				page.wait_for_selector(got_it_button, timeout=2000)
				page.click(got_it_button)
			except:
				pass

			rounds = page.query_selector('xpath=//*[@id="app"]/div/div/div/div/div[1]/div[2]')

			links = rounds.query_selector_all('a[href*="round"]')
			round_links = []
			for link in links:
				href = link.get_attribute('href')
				pairings = f"{href}".replace("standings", "pairings")
				round_links.append(f"{base_url}{pairings}")

			last_round_standings = links[-1].get_attribute('href')
			round_links.append(f"{base_url}{last_round_standings}")
			
			for link in round_links:
				page.goto(link)
				# print(link.split("/"))
				# print(link.split("/")[8])
				# print(link.split("/")[9])

				page.wait_for_url("**", wait_until="networkidle")  # Wait for any new URL

				div_elements = page.query_selector_all('xpath=/html/body/div')
				for div in div_elements:
					extract_table_to_csv(div.inner_text(), f"Round {link.split('/')[8]} {link.split('/')[9]}", link.split('/')[8], f"{year}-{tournament[2]}-{tournament[1]} {tournament[0]}", tournament[3], f"{tournament[0]} {tournament[1]}-{tournament[2]}-{year}", f"{year}-{tournament[2]}-{tournament[1]}")
	except Exception as e:
		print(e)

def login(page):
	consent_button_xpath = "//*[@id=\"ketch-consent-banner\"]/div/div[2]/button[2]"
	page.wait_for_selector(consent_button_xpath)
	page.click(consent_button_xpath)

	login_button_xpath = "//*[@id=\"app\"]/div/div[1]/div[2]/div/div[1]/button"
	page.wait_for_selector(login_button_xpath)
	page.click(login_button_xpath)

	consent_button_xpath = "//*[@id=\"ketch-consent-banner\"]/div/div[2]/button[2]"
	page.wait_for_selector(consent_button_xpath)
	page.click(consent_button_xpath)

	# Enter text in the email input field
	email_input_xpath = "//*[@id=\"email\"]/label/input"
	page.wait_for_selector(email_input_xpath)
	page.fill(email_input_xpath, username)

	password_input_xpath = "//*[@id=\"password\"]/label/input"
	page.wait_for_selector(password_input_xpath)
	page.fill(password_input_xpath, password)

	login_button_xpath = "//*[@id=\"__nuxt\"]/div/div/div[2]/div/div/div/form/button"
	page.wait_for_selector(login_button_xpath)
	page.click(login_button_xpath)

	page.wait_for_url("**", wait_until="networkidle")  # Wait for any new URL