# 📊 Tokopedia Skincare Market Analysis: Moisturizer & Sunscreen

![Dashboard Preview](dash_1.jpg)
![Dashboard Preview](dash_2.jpg)
![Dashboard Preview](dash_3.jpg)

> 🛡️ **Ethical Data & Compliance Notice:**
> This project is made only for **learning and non-commercial purposes**. To follow the platform's Terms of Service (ToS) and protect data privacy, **the raw scraped data, the specific selectors, and personal information (PII) are not uploaded** to this repository. This repository only shares anonymized, aggregated *insights* and synthetic sample data. *(See the full [Disclaimer & Ethical Considerations](#-disclaimer--ethical-considerations) at the bottom.)*

## 📌 Project Overview
An end-to-end data analytics project analyzing the Indonesian skincare market (Sunscreen & Moisturizer) on Tokopedia. This project aims to uncover pricing strategies, market dominance, and the impact of store reputation on sales volume.

## 🎯 Business Questions
1. **Price & Sales:** Does a lower price always lead to higher sales volume?
2. **Reputation & Trust:** Does a high product rating guarantee better sales? How does store type affect customer trust?
3. **Market Dominance:** Which brands, store types, and locations take the biggest share of estimated revenue?

## 📊 Key Business Insights
### 1. Reputation & Trust
- **Rating Saturation:** 91% of products have a rating ≥ 4.8. Rating is no longer a differentiator; it's a baseline requirement.
- **Store Type > Rating:** Official Stores and Power Merchant Pro dominate sales volume, proving that institutional trust outweighs individual product ratings.
### 2. Market Dominance
- **Revenue Concentration:** Official Stores control 91.2% of estimated revenue, despite holding less than 50% of the total product listings.
- **Geographic Focus:** The market is heavily centralized in the Jabodetabek area (Tangerang, Bogor, Bekasi, Jakarta).
### 3. Pricing Strategy
- **Weak Price-Sales Correlation:** The correlation between price and sales volume is only 0.27. Cheaper products do not automatically sell better.
- **The "Sweet Spot":** The highest competition is in the <Rp 50K range, but higher price ranges (Rp 100K-150K) show strong median sales, indicating a viable market for premium mass-market products.

## 🛠️ Tech Stack
- **Data Acquisition:** Python, Playwright (Web Scraping)
- **Data Wrangling:** Python, Pandas, NumPy
- **Business Intelligence:** Microsoft Power BI (DAX, Data Modeling)

## ⚠️ Disclaimer & Ethical Considerations
**Purpose.** This project is made for learning and non-commercial use. The data was taken from public Tokopedia pages (*sunscreen* and *moisturizer* categories, maximum 5 pages per category) in October 2026. This project is not affiliated with, sponsored by, or endorsed by Tokopedia/TikTok. All brands and content belong to their respective owners.

**What is hidden from the code.** To prevent misuse, these parts are left empty on purpose in this repository:
- The target scraping URL (`BASE_URL`)
- The CSS selectors for product name, price, rating, and units sold
- Other specific settings that point to the structure of Tokopedia pages

**What is not uploaded.**

| Original file/folder | Reason |
|---|---|
| `data/raw/` (raw scraped data) | To avoid sharing the data again and to respect the ToS |
| `config.py` (real URL and selectors) | Hidden, see above |
| Transformed datasets that still contain product-level or store-level data | Only aggregated results are published |

**Replacement files that are uploaded.**

| File | Description |
|---|---|
| `verify_env_example.py` | Template with empty values |
| `config_example.py` | Template with empty values |
| `scraper_example.py` | Template with empty values |

**Personal data.** There are no seller or buyer names, contact details, addresses, or review texts. The analysis uses only aggregated numbers.

**User responsibility.** Anyone who runs this code must follow Tokopedia's Terms & Conditions and the applicable laws. The author is not responsible for any misuse of this code. The scraper uses delays between requests and does not try to bypass the site's protection.

## 🚀 Experience the Live Dashboard
Instead of just looking at static screenshots, interact with the data yourself! The dashboard is hosted on Power BI Service.
🔗 [Click here to launch the interactive dashboard](https://bit.ly/vista-tokopedia-dashboard)

*Created by Vista Sasmita Padmanagara | Data Analyst Portfolio*
