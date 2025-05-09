from playwright.sync_api import sync_playwright
import utils
import csv
from pathlib import Path

tournaments = []
with open("CLM_Tournaments.txt", "r") as file:
    tournaments = [line.strip() for line in file]

def main():
	with sync_playwright() as p:
		# browser = p.chromium.launch(headless=False,  args=["--start-maximized"])
		browser = p.chromium.launch(headless=True,  args=["--start-maximized"])

		context, loaded = utils.load_storage(browser)
		page = context.new_page()
		
		for code in tournaments:
			page.goto(f"https://www.circuitoligamagic.com.br/stage-profile/{code}/about")
			page.wait_for_url("**", wait_until="networkidle")

			locator_label = page.locator('span.title', has_text="Data")
			tr_date = locator_label.locator('xpath=following-sibling::*[1]').inner_text().split(",")[0].replace("/", "-")

			locator_label = page.locator('span.title', has_text="Formato")
			tr_format = locator_label.locator('xpath=following-sibling::*[1]').inner_text()

			locator_label = page.locator('span.title', has_text="Torneio")
			tr_name = locator_label.locator('xpath=following-sibling::*[1]').inner_text()
			tr_name = f"{tr_name} - {tr_format} - {tr_date}"
			folder_name = f"CLM {tr_name}"
			
			page.goto(f"https://www.circuitoligamagic.com.br/stage-profile/{code}/rounds")
			page.wait_for_url("**", wait_until="networkidle")

			page.wait_for_selector("div.tw-flex.max-lg\\:tw-mr-4")

			round_container = page.locator("div.tw-flex.max-lg\\:tw-mr-4")
			rounds = round_container.locator("div")
			round_count = rounds.count()
			last_round = round_count

			for i in range(round_count):
				round = rounds.nth(i)
				round.click()
				
				page.wait_for_selector("div.tw-w-full.tw-grid.tw-grid-cols-2.tw-gap-4.lg\\:tw-gap-8")
				grid_container = page.locator("div.tw-w-full.tw-grid.tw-grid-cols-2.tw-gap-4.lg\\:tw-gap-8")
				items = grid_container.locator("div")
				item_count = items.count()
				names = []
				wins = []
				player = 0

				for k in range(item_count):
					item = items.nth(k)
					text = item.inner_text().split('\n')

					found = [name for name in names if name in text[0]]
					if not found:
						if player == 0 and len(text) == 5:
							if text[0] != '' and not text[0].isdigit() and text[0] not in names:
								names.append(text[0])
								wins.append(text[4])
								player = 1
						elif player == 1 and len(text) == 5:
							if text[2] != '' and not text[2].isdigit() and text[2] not in names:
								names.append(text[2])
								wins.append(text[0])
								player = 0

				matches = []
				matches.append(["Round", "Player 1", "Result P1", "Player 1 Wins", "Player 2 Wins", "Result P2", "Player 2", "Format", "Tournament Name", "Date"])
				# standings.append("CLASSIFICAÇÃO", "PONTOS", "V/D/E", "%VPG", "%VJ", "%VJG", tr_format, tr_name, tr_date)
				j = 0
				while j < len(names):
					if j + 1 < len(names):
						
						if wins[j] > wins[j+1]:
							result1, result2 = "Win", "Loss"
						elif wins[j] < wins[j+1]:
							result1, result2 = "Loss", "Win"
						else:
							result1, result2 = "Draw", "Draw"
						
						matches.append([i+1, names[j], result1, wins[j], wins[j+1], result2, names[j+1], tr_format, tr_name, tr_date])
						j += 2
					else:
						matches.append([i+1, names[j], "Win", "2", "0", "Loss", "Bye", tr_format, tr_name, tr_date])
						j += 1

				folder_path = Path(folder_name)
				folder_path.mkdir(parents=True, exist_ok=True)

				file_path = folder_path / f"Round {i+1} pairings.txt"

				with file_path.open("w", encoding="utf-8", newline='') as f:
					writer = csv.writer(f, delimiter='\t')
					writer.writerows(matches)
		
			page.goto(f"https://www.circuitoligamagic.com.br/stage-profile/{code}/classification")
			page.wait_for_url("**", wait_until="networkidle")
			
			page.wait_for_selector("table > tbody")
			rows = page.locator("table > tbody > tr")
			row_count = rows.count()

			standings = []
			standings.append(["CLASSIFICAÇÃO", "NOME", "PONTOS", "V/D/E", "%VPG", "%VJ", "%VJG", tr_format, tr_name, tr_date])

			for i in range(row_count):
				row = rows.nth(i)
				cells = row.locator("td")
				cell_count = cells.count()

				row_data = [cells.nth(j).inner_text().strip() for j in range(cell_count)]
				standings.append([row_data[0], row_data[1], row_data[2], row_data[3].replace(" - ", "/"), row_data[4], row_data[5], row_data[6], tr_format, tr_name, tr_date])
			
			file_path = folder_path / f"Round {last_round} standings.txt"

			with file_path.open("w", encoding="utf-8", newline='') as f:
				writer = csv.writer(f, delimiter='\t')
				writer.writerows(standings)
		
		browser.close()

if __name__ == "__main__":
	main()