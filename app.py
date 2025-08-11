from flask import Flask, request, render_template, send_file
from openai import OpenAI
import openai, io, base64, json
from fpdf import FPDF
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FONT = "ESITC"
FONT_BOLD = "ESITC-Bold"
WIDTH = 1492
HEIGHT = 692
TITLE_SIZE = 400
TITLE_C = 160
TITLE_SPREAD = .5
CELEBRATED_SIZE = 130
CELEBRATED_C = 100
CELEBRATED_SPREAD = .3
DATE_SIZE = 100
DATE_C = 60
DATE_SPREAD = .3
FYT_SIZE = 80
FYT_C = 20
FYT_SPREAD = .3
TABLE_SIZE = 70
TABLE_SPREAD = .2
GUEST_SIZE = 60
GUEST_C = -25
GUEST_D = 90
GUEST_SPREAD = .2
LINE_WIDTH = .5
LINE_D = 5

def draw_bold_text(pdf, x, y, text, font, size, spread=0.3):
    pdf.set_font(font, '', size)
    offsets = [(0,0), (spread,0), (-spread,0), (0,spread), (0,-spread)]
    for dx, dy in offsets:
        pdf.text(x + dx, y + dy, text)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "Nessun file ricevuto"

        file = request.files['image']
        file_path = "uploads/" + file.filename
        file.save(file_path)

        client = OpenAI(api_key=OPENAI_API_KEY)

        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": '''
                            Analizza l’immagine e restituisci un dizionario JSON.
        La prima chiave sarà "Dati", e come valore avrà una lista di 3 elementi che contiene il tipo di evento (matrimonio, 18°, 50°, battesimo o altri..), 
        il nome del festeggiato (possono essere anche più di uno, specie nei matrimoni, in tal caso suddividi con la lettera "&", es. Giulia & Marco) 
        e la data (giorno della settimana, gg mese aa, es. Sabato 15 Luglio 2025). 
        Se non hai i dati, deducili, ma non lasciare vuoto. 
        Il resto deve essere nel formato "Tavolo X" dove X è il numero che identifica un gruppo di ospiti.
        Tutti i nomi sotto, accanto o riferiti visivamente a quel numero/simbolo fanno parte dello stesso tavolo, anche se scritti su colonne diverse,
        e saranno il valore da associare alla chiave, sotto forma di lista. Se ci sono errori ortografici, correggili o deduci il nome.
        Non aggiungere tavoli se non ha ospiti, e fai attenzione a non dimenticarti nessuno. 
                            '''
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        tableau_str = response.choices[0].message.content
        tableau_str = tableau_str.replace("```json\n", "").replace("\n```", "")
        tableau = json.loads(tableau_str)

        max_len = max(len(v) for v in tableau[1:].values())
        for k in tableau:
            tableau[k] += [""] * (max_len - len(tableau[k]))

        pdf = FPDF(format=(WIDTH, HEIGHT))
        pdf.add_page()  # di default bianco
        pdf.image("Sfondo Tableau Magnolia.png", x=0, y=0, w=WIDTH, h=HEIGHT)
        pdf.add_font(FONT, "", "edwardianscriptitc.ttf", uni=True)

        pdf.set_font(FONT, size=TITLE_SIZE)
        title_width = pdf.get_string_width(tableau['Dati'][0])
        draw_bold_text(pdf, x=(WIDTH - title_width) / 2, y=HEIGHT / 2 - TITLE_C,
                       text=tableau['Dati'][0], font=FONT, size=TITLE_SIZE, spread=TITLE_SPREAD)

        pdf.set_font(FONT, size=CELEBRATED_SIZE)
        celebrated_width = pdf.get_string_width(tableau['Dati'][1])
        draw_bold_text(pdf, x=(WIDTH - celebrated_width) / 2, y=HEIGHT / 2 - CELEBRATED_C,
                       text=tableau['Dati'][1], font=FONT, size=CELEBRATED_SIZE, spread=CELEBRATED_SPREAD)

        pdf.set_font(FONT, size=DATE_SIZE)
        date_width = pdf.get_string_width(tableau['Dati'][2])
        draw_bold_text(pdf, x=(WIDTH - date_width) / 2, y=HEIGHT / 2 - DATE_C,
                       text=tableau['Dati'][2], font=FONT, size=DATE_SIZE, spread=DATE_SPREAD)

        pdf.set_font(FONT, size=FYT_SIZE)
        fyt_width = pdf.get_string_width("Find Your Table")
        draw_bold_text(pdf, x=(WIDTH - fyt_width) / 2, y=HEIGHT / 2 - FYT_C,
                       text="Find Your Table", font=FONT, size=FYT_SIZE, spread=FYT_SPREAD)

        line = (len(tableau) - 2) / 2
        for table in list(tableau.keys())[1:]:
            pdf.set_font(FONT, size=TABLE_SIZE)
            guest_width = pdf.get_string_width(table)
            draw_bold_text(pdf, x=(WIDTH - guest_width) / 2 - line * GUEST_D, y=HEIGHT / 2 - GUEST_C,
                           text=table, font=FONT, size=TABLE_SIZE, spread=TABLE_SPREAD)
            pdf.set_line_width(LINE_WIDTH)
            pdf.line((WIDTH - guest_width) / 2 - line * GUEST_D,
                     HEIGHT / 2 - GUEST_C + LINE_D,
                     (WIDTH - guest_width) / 2 - line * GUEST_D + guest_width,
                     HEIGHT / 2 - GUEST_C + LINE_D)
            row = 1
            for guest in tableau[table]:
                pdf.set_font(FONT, size=GUEST_SIZE)
                row += 1
                guest_width = pdf.get_string_width(guest)
                draw_bold_text(pdf, x=(WIDTH - guest_width) / 2 - line * GUEST_D, y=HEIGHT / 2 - row * GUEST_C,
                               text=guest, font=FONT, size=GUEST_SIZE, spread=GUEST_SPREAD)
            line -= 1

        output_path = "outputs/" + file.filename.rsplit(".", 1)[0] + ".pdf"
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
