
import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
from html import unescape
from itertools import zip_longest
from urllib.parse import urljoin

st.set_page_config(
    page_title="Tech & Gaming News",
    page_icon="📰",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: #0b1120;
    color: #f1f5f9;
}

.block-container {
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

.news-label {
    color: #60a5fa;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 3px;
}

.hero-title {
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 850;
    color: #f8fafc;
    margin-bottom: 5px;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 16px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111c30;
    border-color: #26354d;
    border-radius: 16px;
}

a {
    color: #60a5fa !important;
    text-decoration: none !important;
}

a:hover {
    color: #93c5fd !important;
}

div.stButton > button,
div[data-testid="stLinkButton"] a {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.markdown(
    '<div class="news-label">YOUR DAILY TECH BRIEFING</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-title">Tech '
    '<span style="color:#60a5fa">&</span> Gaming.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'The latest stories from the world of technology and gaming.'
    '</div>',
    unsafe_allow_html=True
)

st.write("")
st.divider()


# ---------- SOURCES ----------
sources = {
    "Geekdom": "https://geekdom.gr/category/games/feed",
    "Unboxholics": "https://unboxholics.com/feed",
    "TechBlog":"https://techblog.gr/feed/"
}

st.markdown("### 📰 Latest news")
st.caption("Fresh updates from your favorite sources")

articles_by_source = {}

for source_name, feed_url in sources.items():
    feed = feedparser.parse(feed_url)
    articles_by_source[source_name] = feed.entries[:20]

# Alternate sources so one site does not fill the whole page first
articles = []

for pair in zip_longest(
    articles_by_source["Geekdom"],
    articles_by_source["Unboxholics"],
    articles_by_source["TechBlog"]
):
    for source_name, article in zip(
        ("Geekdom", "Unboxholics","TechBlog"), pair
    ):
        if article is not None:
            articles.append((source_name, article))

# ---------- DISPLAY NEWS ----------
if articles:
    columns = st.columns(3)

    for i, (source_name, article) in enumerate(articles):

        title = article.get("title", "Untitled article")
        link = article.get("link", "")
        

        # Get description from the available RSS fields
        description = (
            article.get("summary")
            or article.get("description")
            or article.get("subtitle")
            or ""
        )

        description = BeautifulSoup(
            unescape(description), "html.parser"
        ).get_text(" ", strip=True)

        # ---------- GET IMAGE ----------
        image_url = None

        # First try the image provided in RSS
        enclosures = article.get("enclosures", [])

        for enclosure in enclosures:
            candidate = enclosure.get("href") or enclosure.get("url")
            if candidate and candidate.startswith(("http://", "https://")):
                image_url = candidate
                break

        # Then try the article's Open Graph image
        if not image_url and link:
            try:
                response = requests.get(
                    link,
                    timeout=8,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                og_image = soup.find("meta", property="og:image")

                if og_image and og_image.get("content"):
                    image_url = urljoin(
                        link, og_image["content"]
                    )

            except requests.RequestException:
                pass

        # ---------- CARD ----------
        with columns[i % 3]:
            with st.container(border=True):

                st.caption(f"🎮  {source_name.upper()}")

                if image_url:
                    st.image(
                        image_url,
                        use_container_width=True
                    )
                else:
                    st.caption("Image unavailable")

                st.markdown(f"### [{title}]({link})")

                if description:
                    if len(description) > 250:
                        description = (
                            description[:250].rsplit(" ", 1)[0]
                            + "..."
                        )
                    st.write(description)
                else:
                    st.caption("Open the article to read more.")
              
              
                if link:
                    st.link_button(
                        "Read full article ↗",
                        link,
                        use_container_width=True
                    )
                else:
                    st.link_button("Read full article ↗", "https://unboxholics.com/",  use_container_width=True)
                    

else:
    st.warning("No news articles were found. Try again later.")
