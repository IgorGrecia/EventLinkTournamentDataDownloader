from playwright.sync_api import sync_playwright
import utils

tournaments = []
# tournaments.append(["Weekly Pauper", "25", "03", 'Pauper'])
tournaments.append(["Weekly Modern", "26", "03", 'Modern'])
# tournaments.append(["Biweekly Pioneer", "13", "03", 'Pioneer'])
# tournaments.append(["Mont Standard Showdown", "21", "03", 'Standard'])

def main():
	with sync_playwright() as p:
		# browser = p.chromium.launch(headless=False,  args=["--start-maximized"])
		browser = p.chromium.launch(headless=True,  args=["--start-maximized"])

		context, loaded = utils.load_storage(browser)

		page = context.new_page()
		
		# Navigate to the EventLink page
		page.goto("https://eventlink.wizards.com/")

		if loaded == False:
			utils.login(page)
			# save_storage(context)

		for tournament in tournaments:
			page.wait_for_url("**", wait_until="networkidle")
			page.goto("https://eventlink.wizards.com/")
			try:
				got_it_button = "//*[@id=\"global-api-errors\"]/div/p[2]/tt"
				page.wait_for_selector(got_it_button, timeout=5000)
				page.goto("https://eventlink.wizards.com/")
				page.wait_for_url("**", wait_until="networkidle")
			except:
				pass
			utils.get_weekly_tournament(tournament, page)
		
		browser.close()

if __name__ == "__main__":
	main()