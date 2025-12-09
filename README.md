
The **AI-Driven Retail Creative Compliance Builder** is a web-based tool that automates the generation and validation of marketing creatives according to retailer-specific brand and format guidelines. It enables advertisers to quickly produce compliant, professional-quality ads by combining packshots, logos, and headlines, while automatically checking each design against compliance rules.

---

## Features

* **Creative Generation:** Upload a packshot, logo, and headline to automatically generate ad creatives.
* **Compliance Checking:** Validates safe-zone limits, packshot proportions, font sizes, and prohibited words.
* **Instant Preview:** Displays the generated creative and compliance report in real time.
* **Multi-Format Support:** Generates creatives for both feed (1200×1200) and story (1080×1920) formats.
* **Integrated Frontend:** Uses a lightweight HTML, CSS, and JavaScript interface embedded within FastAPI.
* **Extensible Architecture:** Designed for future AI enhancements such as background removal and layout generation.

---

## Tech Stack

* **Backend:** FastAPI (Python), Uvicorn
* **Frontend:** HTML5, CSS3, JavaScript
* **Image Processing:** Pillow (PIL)
* **Middleware:** CORS Middleware
* **Compliance Engine:** Python-based JSON rules
* **Future Enhancements:** React, Background Removal (rembg), LLM Copy Validator

---

## Installation and Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/retail-creative-builder.git
   cd retail-creative-builder
   ```

2. **Install dependencies**

   ```bash
   pip install fastapi uvicorn pillow python-multipart
   ```

3. **Run the application**

   ```bash
   python app.py
   ```

   or

   ```bash
   uvicorn app:app --reload
   ```

4. **Access the application**
   Open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Example Usage

**Input:**

* Packshot: Product image (PNG/JPG)
* Logo: Brand logo (optional)
* Headline: Example text such as “New Season Offers”
* Format: Feed or Story

**Output:**

* Generated creative image
* Compliance report, for example:

  ```
  Status: PASS
  Packshot %: 0.42
  Prohibited words: None
  ```

---

## Project Structure

```
retail-creative-builder/
│
├── app.py               # Main FastAPI backend and embedded frontend
├── README.md            # Project documentation
└── /tmp/                # Folder where generated creatives are stored temporarily
```

---

## Future Scope

* Integration of background removal and automatic color extraction
* AI-based layout suggestion and creative optimization
* Retailer-specific rule sets stored in JSON configuration files
* Copy validation using LLMs to detect prohibited or misleading claims
* Advanced React-based drag-and-drop creative builder frontend



Would you like me to write a **short GitHub project description and tags** (e.g., “AI-powered creative generation and compliance engine built with FastAPI”) to add below your repository title?
