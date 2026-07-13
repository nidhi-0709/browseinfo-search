import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


headers = {
    "User-Agent": "Mozilla/5.0"
}


BASE_URL = "https://apps.odoo.com"

LIST_URL = (
    "https://apps.odoo.com/apps/modules/"
    "browse/page/{}?search=browseinfo"
)


modules = []
seen_urls = set()
failed_urls = []


# --------------------------------------------------------
# Request Function (Retry)
# --------------------------------------------------------

def get_page(url):

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            if response.status_code == 200:
                return response.text

        except Exception:
            pass

        time.sleep(2)

    failed_urls.append(url)

    return ""



# --------------------------------------------------------
# Extract Module Details
# --------------------------------------------------------

def extract_module_details(module):

    try:

        html = get_page(module["URL"])

        if not html:
            return module


        soup = BeautifulSoup(
            html,
            "lxml"
        )


        # -------------------------
        # Category
        # -------------------------

        breadcrumb = soup.select(
            "ol.breadcrumb li"
        )

        if len(breadcrumb) >= 2:

            module["Category"] = (
                breadcrumb[-2]
                .get_text(strip=True)
            )



        # -------------------------
        # Description
        # -------------------------

        description = []


        for tag in soup.select(
            ".oe_structure p, "
            ".oe_structure li, "
            ".oe_structure h2, "
            ".oe_structure h3"
        ):

            text = tag.get_text(
                " ",
                strip=True
            )

            if len(text) > 20:
                description.append(text)


        module["Description"] = "\n".join(
            description
        )



        # -------------------------
        # Features
        # -------------------------

        features = []


        feature_tab = soup.find(
            "div",
            id="feature_tab"
        )


        # fallback
        if not feature_tab:

            feature_tab = soup.find(
                class_="oe_structure"
            )


        if feature_tab:


            headings = feature_tab.find_all(
                ["h2", "h3"]
            )


            for heading in headings:

                title = heading.get_text(
                    " ",
                    strip=True
                )


                next_text = ""


                p = heading.find_next(
                    "p"
                )


                if p:

                    next_text = p.get_text(
                        " ",
                        strip=True
                    )


                if title:

                    features.append(
                        f"{title}: {next_text}"
                    )


        module["Features"] = "\n".join(
            features
        )



        # -------------------------
        # Future Semantic Fields
        # -------------------------

        module["UseCases"] = ""

        module["Industry"] = ""

        module["Workflow"] = ""

        module["Integration"] = ""



        # -------------------------
        # Search Text for Embedding
        # -------------------------

        module["SearchText"] = f"""

        Module Name:
        {module.get('Title','')}

        Category:
        {module.get('Category','')}

        Summary:
        {module.get('Summary','')}

        Description:
        {module.get('Description','')}

        Features:
        {module.get('Features','')}

        Business Use Cases:
        {module.get('UseCases','')}

        Industry:
        {module.get('Industry','')}

        Workflow:
        {module.get('Workflow','')}

        Integration:
        {module.get('Integration','')}

        """

        module["SearchText"] = (
            module["SearchText"]
            .replace("\n\n", "\n")
            .strip()
        )


    except Exception as e:

        print(
            "Error:",
            module["URL"],
            e
        )


    return module




# --------------------------------------------------------
# Find Total Pages
# --------------------------------------------------------

print("Finding total pages...")


html = get_page(
    LIST_URL.format(1)
)


soup = BeautifulSoup(
    html,
    "lxml"
)


total_pages = 1


for a in soup.select(
    "ul.pagination a"
):

    text = a.get_text(
        strip=True
    )

    if text.isdigit():

        total_pages = max(
            total_pages,
            int(text)
        )


print(
    "Total Pages:",
    total_pages
)




# --------------------------------------------------------
# Scrape Modules
# --------------------------------------------------------

sr = 1


for page in range(
    1,
    total_pages + 1
):


    print(
        f"\nScraping Page {page}/{total_pages}"
    )


    html = get_page(
        LIST_URL.format(page)
    )


    soup = BeautifulSoup(
        html,
        "lxml"
    )


    apps = soup.select(
        "div.loempia_app_entry"
    )


    page_modules = []


    for app in apps:


        try:

            title = app.find(
                "h5"
            ).get_text(
                strip=True
            )


            summary_tag = app.find(
                "p",
                class_="loempia_panel_summary"
            )


            summary = ""


            if summary_tag:

                summary = summary_tag.get_text(
                    " ",
                    strip=True
                )


            href = app.find(
                "a"
            )["href"]


            url = BASE_URL + href



            if url in seen_urls:
                continue


            seen_urls.add(url)



            page_modules.append({

                "Sr No": sr,

                "Page": page,

                "Source": "BrowseInfo",

                "Title": title,

                "Summary": summary,

                "Category": "",

                "Description": "",

                "Features": "",

                "UseCases": "",

                "Industry": "",

                "Workflow": "",

                "Integration": "",

                "SearchText": "",

                "URL": url

            })


            sr += 1



        except Exception as e:

            print(
                "List Error:",
                e
            )




    print(
        "Modules Found:",
        len(page_modules)
    )



    # Parallel extraction

    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:


        futures = [

            executor.submit(
                extract_module_details,
                module
            )

            for module in page_modules

        ]


        for future in as_completed(futures):

            module = future.result()


            modules.append(
                module
            )


            print(
                "Completed:",
                module["Title"]
            )





# --------------------------------------------------------
# Save JSON
# --------------------------------------------------------

with open(
    "browseinfo_modules.json",
    "w",
    encoding="utf-8"
) as f:


    json.dump(
        modules,
        f,
        indent=4,
        ensure_ascii=False
    )




# --------------------------------------------------------
# Save Excel
# --------------------------------------------------------

df = pd.DataFrame(
    modules
)


df = df.sort_values(
    "Sr No"
)


df.to_excel(
    "browseinfo_modules.xlsx",
    index=False
)




# --------------------------------------------------------
# Save Failed URLs
# --------------------------------------------------------

with open(
    "failed_urls.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        failed_urls,
        f,
        indent=4
    )



print("\n====================")
print("Finished")
print(
    "Total Modules:",
    len(modules)
)
print(
    "Failed URLs:",
    len(failed_urls)
)
print("====================")