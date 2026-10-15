import os
import re
import requests
from slugify import slugify
from markdownify import markdownify as md

BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
OUTPUT_DIR = "./articles_md"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_and_convert_html(html_content: str, domain: str = "https://support.optisigns.com") -> str:
    """
    Chuẩn hóa HTML và chuyển đổi sang Markdown:
    - Giữ code block, bảng, heading
    - Chuẩn hóa link nội bộ thành relative link
    """
    if not html_content:
        return ""

    # Chuẩn hóa link tuyệt đối trỏ về domain thành relative link
    html_content = html_content.replace(domain, "")

    # Chuyển đổi sang Markdown với định dạng ATX (#, ##, ###)
    markdown_text = md(
        html_content,
        heading_style="ATX",
        code_language="",
        strip=["script", "style", "form"]
    )

    # Loại bỏ khoảng trắng thừa liên tiếp
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()
    return markdown_text

def fetch_and_save_articles(target_count: int = 30):
    current_url = f"{BASE_URL}?per_page=30"
    articles_saved = 0

    while current_url and articles_saved < target_count:
        print(f"Đang tải: {current_url}")
        res = requests.get(current_url, headers={"User-Agent": "Mozilla/5.0"})
        
        if res.status_code != 200:
            print(f"Lỗi gọi API: {res.status_code}")
            break

        data = res.json()
        articles = data.get("articles", [])

        for art in articles:
            if articles_saved >= target_count:
                break

            title = art.get("title", "untitled")
            slug = slugify(title)
            body_html = art.get("body", "")
            web_url = art.get("html_url", "")
            
            # Chuyển đổi nội dung
            markdown_body = clean_and_convert_html(body_html)

            # Thêm metadata (YAML frontmatter) phục vụ cho RAG / SSG
            content = (
                f"---\n"
                f"title: \"{title}\"\n"
                f"id: {art.get('id')}\n"
                f"source_url: \"{web_url}\"\n"
                f"updated_at: \"{art.get('updated_at')}\"\n"
                f"---\n\n"
                f"# {title}\n\n"
                f"{markdown_body}\n"
            )

            file_path = os.path.join(OUTPUT_DIR, f"{slug}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            articles_saved += 1
            print(f"[{articles_saved}/{target_count}] Đã lưu: {slug}.md")

        # Phân trang tự động
        current_url = data.get("next_page")

    print(f"\nHoàn tất: Đã xuất {articles_saved} bài viết ra thư mục '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    fetch_and_save_articles(target_count=30)