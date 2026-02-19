from bs4 import BeautifulSoup

file_path = r"d:\fake review detection\amazon_debug.html"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    
    titles = soup.select('[data-hook="review-title"]')
    print(f"Review titles found: {len(titles)}")
    
    if len(titles) > 0:
        first_title = titles[0]
        parent = first_title.find_parent('div')
        print(f"Parent of first title: {parent.name} | Attributes: {parent.attrs}")
        
        # Check grandparent too just in case
        grandparent = parent.find_parent('div')
        print(f"Grandparent of first title: {grandparent.name} | Attributes: {grandparent.attrs}")

    bodies = soup.select('[data-hook="review-body"]')
    print(f"Review bodies found: {len(bodies)}")

except Exception as e:
    print(f"Error: {e}")
