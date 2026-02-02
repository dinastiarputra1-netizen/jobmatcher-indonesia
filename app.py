import os, re, fitz, random, time
import cloudscraper
import streamlit as st
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="JobMatcher Indonesia", layout="wide")

# --- DATA MASTER (TIDAK BERUBAH) ---
MASTER_SKILLS = [
    'python', 'javascript', 'sql', 'php', 'react', 'java', 'excel', 'pemasaran', 
    'accounting', 'photoshop', 'figma', 'canva', 'sales', 'negotiation', 'leadership',
    'management', 'seo', 'digital marketing', 'social media', 'copywriting', 'tableau',
    'power bi', 'docker', 'kubernetes', 'aws', 'flutter', 'swift', 'android', 'laravel'
]

INDUSTRY_LIST = [
    'developer', 'engineer', 'admin', 'marketing', 'sales', 'accountant', 'designer',
    'manager', 'staff', 'hrd', 'driver', 'guru', 'perawat', 'chef', 'content creator',
    'data scientist', 'analyst', 'security', 'operator', 'teknisi', 'arsitek'
]

# --- FUNGSI INTI (TIDAK BERUBAH) ---
def get_scraper():
    return cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )

def extract_smart_keyword(text):
    text = text.lower()
    for word in INDUSTRY_LIST:
        if word in text: return word
    words = re.findall(r'\w+', text)
    filtered = [w for w in words if len(w) > 4 and w not in ['dengan', 'yang', 'untuk', 'dalam', 'cv', 'curriculum', 'vitae']]
    return Counter(filtered).most_common(1)[0][0] if filtered else "kerja"

def scrape_source_jora(keyword, location):
    jobs = []
    try:
        scraper = get_scraper()
        url = f"https://id.jora.com/j?q={keyword}&l={location}"
        time.sleep(random.uniform(1, 3)) 
        response = scraper.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.select('.job-card, .job-container, [class*="job-card"]')
            for card in cards:
                title_tag = card.select_one('.job-title, .title a, [data-automation="job-title"]')
                if title_tag:
                    raw_link = title_tag.get('href') or (title_tag.find('a').get('href') if title_tag.find('a') else None)
                    if not raw_link: continue
                    full_link = f"https://id.jora.com{raw_link}" if raw_link.startswith('/') else raw_link
                    jobs.append({
                        "title": title_tag.get_text(strip=True),
                        "company": card.select_one('.company, .job-company').get_text(strip=True) if card.select_one('.company, .job-company') else "Perusahaan Indonesia",
                        "location": card.select_one('.location, .job-location').get_text(strip=True) if card.select_one('.location, .job-location') else location,
                        "desc": card.select_one('.job-abstract, .summary').get_text(strip=True) if card.select_one('.job-abstract, .summary') else "",
                        "link": full_link
                    })
    except Exception as e:
        st.error(f"Jora Scrape Error: {e}")
    return jobs

def scrape_source_careerjet(keyword, location):
    jobs = []
    try:
        scraper = get_scraper()
        url = f"https://www.careerjet.co.id/cari-kerja?s={keyword}&l={location}"
        response = scraper.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for card in soup.select('.job, .result'):
                title_tag = card.select_one('h2 a, .title a')
                if title_tag:
                    raw_link = title_tag.get('href')
                    full_link = f"https://www.careerjet.co.id{raw_link}" if raw_link.startswith('/') else raw_link
                    jobs.append({
                        "title": title_tag.get_text(strip=True),
                        "company": card.select_one('.company_name, .company').get_text(strip=True) if card.select_one('.company_name, .company') else "Careerjet Partner",
                        "location": card.select_one('.location').get_text(strip=True) if card.select_one('.location') else location,
                        "desc": card.select_one('.desc, .description').get_text(strip=True) if card.select_one('.desc, .description') else "",
                        "link": full_link
                    })
    except Exception as e:
        st.error(f"Careerjet Error: {e}")
    return jobs

def generate_pdf(data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 750, f"Laporan Lowongan AI: {data['query']}")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, f"Lokasi: {data['loc']} | Ditemukan: {len(data['jobs'])} posisi")
    p.line(50, 725, 550, 725)
    
    y = 700
    for j in data['jobs'][:25]:
        if y < 80: p.showPage(); y = 750
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, f"{j['title']} ({j['score']}%)")
        p.setFont("Helvetica", 10)
        p.drawString(50, y-15, f"{j['company']} - {j['location']}")
        y -= 45
    p.save()
    buffer.seek(0)
    return buffer

# --- STREAMLIT UI ---
def main():
    st.title("💼 JobMatcher Indonesia")
    st.markdown("Cari lowongan kerja yang paling cocok dengan CV Anda menggunakan AI.")

    with st.sidebar:
        st.header("Pengaturan")
        location = st.text_input("Lokasi Pencarian", "Indonesia")
        cv_file = st.file_uploader("Unggah CV (PDF)", type=["pdf"])
        search_button = st.button("Analisa & Cari Lowongan")

    if cv_file and search_button:
        with st.spinner("Mengekstrak teks dan mencari lowongan..."):
            # Ekstrak Teks PDF
            try:
                with fitz.open(stream=cv_file.read(), filetype="pdf") as doc:
                    cv_text = "".join([page.get_text() for page in doc]).lower()
            except Exception as e:
                st.error(f"Gagal membaca PDF: {e}")
                return

            # Jalankan Logika Pencarian
            query = extract_smart_keyword(cv_text)
            results = scrape_source_jora(query, location) + scrape_source_careerjet(query, location)
            
            if not results:
                fallback_query = "lowongan"
                results = scrape_source_careerjet(fallback_query, location)
                query = f"{query} (umum)"

            # Proses Scoring
            user_skills = [s for s in MASTER_SKILLS if s in cv_text]
            final_list = []
            
            if results:
                seen = set()
                unique_jobs = [j for j in results if not ((j['title'] + j['company']).lower() in seen or seen.add((j['title'] + j['company']).lower()))]

                if unique_jobs:
                    docs = [cv_text] + [f"{j['title']} {j['desc']}" for j in unique_jobs]
                    tfidf = TfidfVectorizer(stop_words='english').fit_transform(docs)
                    scores = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
                    
                    for i, j in enumerate(unique_jobs):
                        job_full_text = (j['title'] + " " + j['desc']).lower()
                        missing = [s for s in MASTER_SKILLS if s in job_full_text and s not in user_skills]
                        j['score'] = round(min(scores[i] * 500 + 25, 99.8), 1)
                        j['missing_skills'] = missing[:5]
                        final_list.append(j)

            final_list = sorted(final_list, key=lambda x: x['score'], reverse=True)

            # --- TAMPILKAN HASIL ---
            if final_list:
                st.success(f"Ditemukan {len(final_list)} lowongan untuk kata kunci: **{query}**")
                
                # Tombol Download PDF
                pdf_data = generate_pdf({'jobs': final_list, 'query': query, 'loc': location})
                st.download_button(
                    label="📥 Download Laporan PDF",
                    data=pdf_data,
                    file_name="Laporan_Kerja.pdf",
                    mime="application/pdf"
                )

                # Grid Tampilan Kartu
                cols = st.columns(3)
                for idx, job in enumerate(final_list):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.subheader(f"{job['score']}% Match")
                            st.markdown(f"**{job['title']}**")
                            st.caption(f"{job['company']} | {job['location']}")
                            
                            if job['missing_skills']:
                                st.markdown("**Missing Skills:**")
                                st.write(", ".join(job['missing_skills']))
                            
                            st.link_button("Lamar Sekarang", job['link'])
            else:
                st.warning("Tidak ditemukan lowongan yang cocok.")

if __name__ == "__main__":
    main()