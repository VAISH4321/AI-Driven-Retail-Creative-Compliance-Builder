from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import io, os, uuid, math

app = FastAPI(title="Retail Creative Builder - Single File Demo")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Retailer rules
RETAILER_RULES = {
    "default": {
        "safe_zone_pct": 0.05,
        "max_packshot_pct": 0.6,
        "min_font_px": 18,
        "prohibited_words": ["free", "guarantee", "alcohol"]
    }
}

def read_imagefile(file_bytes):
    return Image.open(io.BytesIO(file_bytes)).convert("RGBA")

def save_image(img, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, format='PNG')

def compliance_check(canvas_w, canvas_h, packshot_size, headline, retailer_key="default"):
    rules = RETAILER_RULES.get(retailer_key, RETAILER_RULES["default"])
    pack_w, pack_h = packshot_size
    pack_area = pack_w * pack_h
    canvas_area = canvas_w * canvas_h
    pack_pct = pack_area / canvas_area if canvas_area>0 else 0.0

    safe_margin = rules["safe_zone_pct"]
    safe_pixels = {
        "left": int(canvas_w * safe_margin),
        "right": int(canvas_w * safe_margin),
        "top": int(canvas_h * safe_margin),
        "bottom": int(canvas_h * safe_margin)
    }

    pack_ok = pack_pct <= rules["max_packshot_pct"]

    headline_lower = headline.lower()
    bad_words = [w for w in rules["prohibited_words"] if w in headline_lower]
    bad_copy = len(bad_words) > 0

    report = {
        "packshot_pct": round(pack_pct, 3),
        "packshot_ok": pack_ok,
        "prohibited_words_found": bad_words,
        "headline_ok": not bad_copy,
        "safe_zone_px": safe_pixels
    }
    report["status"] = "PASS" if (pack_ok and not bad_copy) else "FAIL"
    return report

# ---------------- Frontend ----------------
@app.get("/", response_class=HTMLResponse)
def frontend():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Creative Builder</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                margin-top: 50px;
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                width: 400px;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 20px;
            }
            input[type="file"], input[type="text"], select {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 6px;
                border: 1px solid #ccc;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 10px;
                transition: 0.3s;
            }
            button:hover {
                background-color: #45a049;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                border-radius: 6px;
                background: #eef2f5;
                font-weight: bold;
                color: #333;
                white-space: pre-line;
            }
            #generatedImage {
                display: block;
                margin: 20px auto 0 auto;
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Retail Creative Builder</h1>
            <form id="creativeForm">
                Packshot: <input type="file" name="packshot" required><br>
                Logo (optional): <input type="file" name="logo"><br>
                Headline: <input type="text" name="headline" placeholder="Enter headline"><br>
                Format:
                <select name="format_name">
                    <option value="feed">Feed</option>
                    <option value="story">Story</option>
                </select><br>
                <button type="submit">Generate Creative</button>
            </form>
            <div id="result"></div>
            <img id="generatedImage" src="" alt="">
        </div>
        <script>
            const form = document.getElementById("creativeForm");
            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                const data = new FormData(form);
                document.getElementById("result").innerText = "Processing...";
                const resp = await fetch("/api/generate_layout", { method: "POST", body: data });
                const json = await resp.json();
                if(json.error){
                    document.getElementById("result").innerText = "Error: " + json.error;
                } else {
                    document.getElementById("result").innerText = "Status: " + json.compliance.status
                        + "\\nPackshot %: " + json.compliance.packshot_pct
                        + "\\nProhibited words: " + (json.compliance.prohibited_words_found.join(", ") || "None");
                    document.getElementById("generatedImage").src = "/api/get_image?path=" + encodeURIComponent(json.image_path);
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content




# ---------------- Backend ----------------
@app.post("/api/generate_layout")
async def generate_layout(
    packshot: UploadFile = File(...),
    logo: UploadFile = File(None),
    headline: str = Form(""),
    retailer: str = Form("default"),
    format_name: str = Form("feed")
):
    pack_bytes = await packshot.read()
    try: pimg = read_imagefile(pack_bytes)
    except: return JSONResponse({"error": "invalid packshot"}, status_code=400)

    logo_img = None
    if logo:
        try: logo_img = read_imagefile(await logo.read())
        except: logo_img = None

    W,H = (1200,1200) if format_name=="feed" else (1080,1920)
    canvas = Image.new("RGBA",(W,H),(255,255,255,255))
    draw = ImageDraw.Draw(canvas)

    # Packshot resize
    target_area = int(W*H*0.45)
    p_w,p_h = pimg.size
    p_ratio = p_w/p_h if p_h!=0 else 1
    new_h = max(1,int(math.sqrt(target_area/p_ratio)))
    new_w = max(1,int(new_h*p_ratio))
    p_resized = pimg.resize((new_w,new_h),Image.LANCZOS)
    canvas.paste(p_resized, ((W-new_w)//2,(H-new_h)//2), p_resized)

    # Logo top-left
    if logo_img:
        l_w = int(W*0.18)
        lw,lh = logo_img.size
        l_ratio = lw/lh if lh!=0 else 1
        logo_resized = logo_img.resize((l_w,max(1,int(l_w/l_ratio))),Image.LANCZOS)
        canvas.paste(logo_resized,(int(W*0.05),int(H*0.05)),logo_resized)

    # Headline
    font_size=36
    try: font=ImageFont.truetype("DejaVuSans-Bold.ttf",font_size)
    except: font=ImageFont.load_default()
    bbox = draw.textbbox((0, 0), headline, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    text_x,text_y = (W-text_w)//2,H-int(H*0.12)
    draw.rectangle([(text_x-10,text_y-10),(text_x+text_w+10,text_y+text_h+10)],fill=(0,0,0,150))
    draw.text((text_x,text_y),headline,font=font,fill=(255,255,255,255))

    out_id = str(uuid.uuid4())[:8]
    out_path = f"/tmp/creative_{out_id}.png"
    save_image(canvas,out_path)
    report = compliance_check(W,H,p_resized.size,headline,retailer)
    return JSONResponse({"image_path": out_path,"compliance": report})

@app.get("/api/get_image")
def get_image(path: str):
    if os.path.exists(path):
        return FileResponse(path,media_type="image/png")
    return JSONResponse({"error":"file missing"},status_code=404)

if __name__=="__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

