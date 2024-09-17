"""
VENNEKONTAKT er et lite program som holder oversikt over når du sist hadde kontakt med vennene dine.
Programmet er skrevet i Python, og bruker SQLite for databasehåndtering og wxPython for GUI.
Forhåpentligvis vil programmet gjøre det lettere å pleie vennskapene når livet blir travelt. :)
"""

import sqlite3
from datetime import datetime
import wx

# database setup
def setup_database():
    venner = sqlite3.connect("venner.db")
    v = venner.cursor()
    v.execute("""
    CREATE TABLE IF NOT EXISTS venner (
        id INTEGER PRIMARY KEY,
        navn TEXT NOT NULL,
        siste_kontakt DATE NOT NULL)
    """)
    venner.commit()
    return venner, v

# panel for bakgrunnsbilde
class ImagePanel(wx.Panel):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.image = wx.Image(image_path).ConvertToBitmap()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.image, 0, 0, True)

# hovedprogram
class Vennekontakt(wx.Frame):
    def __init__(self, *args, **kw):
        super(Vennekontakt, self).__init__(*args, **kw)
        self.venner, self.v = setup_database()
        self.SetTitle("Vennekontakt")
        self.SetSize(650, 450)

        # panel for innholdet
        self.panel = wx.Panel(self)               
        self.panel.SetBackgroundColour(wx.Colour(0, 0, 0))

        # hovedboks
        self.main = wx.BoxSizer(wx.VERTICAL)

        # header
        self.header = wx.BoxSizer(wx.VERTICAL)
        self.bg_panel = ImagePanel(self.panel, "bg.png")
        self.bg_panel.SetMinSize((-1, 80))
        self.header.Add(self.bg_panel, 0, wx.EXPAND | wx.ALL, 0)
        self.main.Add(self.header, 0, wx.EXPAND | wx.ALL, 5)
        self.vertikal_boks = wx.BoxSizer(wx.VERTICAL)     # vertikal boks

        # boks for teksten
        graa = wx.Colour(40, 40, 40)
        self.tekstboks = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(600, 200))
        self.tekstboks.SetValue("Hei!\n\nJeg hjelper deg med å holde oversikt over når du hadde kontakt med vennene dine sist.\nKlikk på en av knappene under:\n")
        self.tekstboks.SetBackgroundColour(wx.Colour(200, 200, 200))
        self.tekstboks.SetForegroundColour(graa)

        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas")
        self.tekstboks.SetFont(font)
        
        self.vertikal_boks.Add(self.tekstboks, 0, wx.ALL | wx.EXPAND, 20)

        knapp_boks = wx.BoxSizer(wx.HORIZONTAL)   # horisontal boks for knapper

        # knapper med kommandoer
        self.lag_knapp("Legg til venn", self.legg_til, knapp_boks)
        self.lag_knapp("Endre dato", self.endre_dato, knapp_boks)
        self.lag_knapp("Vis venner", self.vis_venner, knapp_boks)
        self.lag_knapp("Sjekk siste kontakt", self.sjekk, knapp_boks)
        self.lag_knapp("Slett venn", self.slett, knapp_boks)
        self.lag_knapp("Avslutt", self.avslutt, knapp_boks)

        self.vertikal_boks.Add(knapp_boks, 0, wx.ALL | wx.CENTER, 5)
        self.main.Add(self.vertikal_boks, 1, wx.EXPAND)
        self.panel.SetSizer(self.main)
        self.bg_panel.Bind(wx.EVT_PAINT, self.bg_panel.OnPaint)

        self.Show()

    # knapper
    def lag_knapp(self, label, handler, knapp_boks):
        knapp = wx.Button(self.panel, label=label, style=wx.NO_BORDER)
        knapp.Bind(wx.EVT_BUTTON, handler)
        
        lysgraa = wx.Colour(148, 148, 148)  # bg
        roed = wx.Colour(174, 124, 124)     # bg hover
        hvit = wx.Colour(255, 255, 255)     # tekstfarge
        mork = wx.Colour(40, 40, 40)        # tekstfarge hover

        knapp.SetBackgroundColour(lysgraa)
        knapp.SetForegroundColour(mork)
        font = wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Consolas")
        knapp.SetFont(font)

        # hovering
        knapp.Bind(wx.EVT_ENTER_WINDOW, lambda event: (knapp.SetBackgroundColour(roed), knapp.SetForegroundColour(hvit)))
        # ikke hovering
        knapp.Bind(wx.EVT_LEAVE_WINDOW, lambda event: (knapp.SetBackgroundColour(lysgraa), knapp.SetForegroundColour(mork)))

        knapp_boks.Add(knapp, 0, wx.ALL | wx.CENTER, 5)

    # kommandoer
    def legg_til(self, event):
        navn = wx.GetTextFromUser("Navn på venn:", "Legg til venn")
        if navn:
            self.v.execute("SELECT * FROM venner WHERE navn = ?", (navn,))
            if self.v.fetchone():
                melding = f"{navn} er allerede lagt til."
            else:
                self.v.execute("INSERT INTO venner (navn, siste_kontakt) VALUES (?, ?)", (navn, datetime.now().strftime("%d.%m.%Y")))
                self.venner.commit()
                melding = f"Lagt til {navn}."

            tekst = self.tekstboks.GetValue()
            self.tekstboks.SetValue(f"{tekst}\n{melding}\n")

    def endre_dato(self, event):
        navn = wx.GetTextFromUser("Navn på venn:", "Endre dato")
        if navn:
            ny_dato = wx.GetTextFromUser("Ny dato (DD.MM.YYYY):", "Ny dato")
            self.v.execute("UPDATE venner SET siste_kontakt = ? WHERE navn = ?", (ny_dato, navn))
            self.venner.commit()
            melding = f"Oppdatert dato for {navn}."

            tekst = self.tekstboks.GetValue()
            self.tekstboks.SetValue(f"{tekst}\n{melding}\n")

    def vis_venner(self, event):
        self.v.execute("SELECT navn, siste_kontakt FROM venner")
        venner_oversikt = self.v.fetchall()
        tekst = self.tekstboks.GetValue()
        if venner_oversikt:
            ny_tekst = "\n".join([f"Navn: {venn[0]}, Siste kontakt: {venn[1]}" for venn in venner_oversikt])
            oppdatert_tekst = f"{tekst}\n{ny_tekst}\n"
        else:
            oppdatert_tekst = f"{tekst}\nIngen venner er lagt til.\n"
        self.tekstboks.SetValue(oppdatert_tekst)

    def sjekk(self, event):
        navn = wx.GetTextFromUser("Navn på venn som skal sjekkes:", "Sjekk kontakt")
        if navn:
            self.v.execute("SELECT navn, siste_kontakt FROM venner WHERE navn = ?", (navn,))
            venn = self.v.fetchone()
            if venn:
                siste_kontakt = datetime.strptime(venn[1], "%d.%m.%Y")
                forskjell = datetime.now() - siste_kontakt
                totalt_dager = forskjell.days

                if totalt_dager < 7:
                    melding = f"Det er {totalt_dager} dager siden du snakket med {navn} sist."
                else:
                    aar = totalt_dager // 365
                    gjenv_dager = totalt_dager % 365
                    mnd = gjenv_dager // 30
                    gjenv_dager %= 30
                    uker = gjenv_dager // 7
                    dager = gjenv_dager % 7
                    tid_deler = []
                    if aar > 0:
                        tid_deler.append(f"{aar} år")
                    if mnd > 0:
                        tid_deler.append(f"{mnd} måned(er)")
                    if uker > 0:
                        tid_deler.append(f"{uker} uke(r)")
                    tid_deler.append(f"{dager} dag(er)")
                    melding = f"Det er {', '.join(tid_deler)} siden sist du snakket med {navn}."

                tekst = self.tekstboks.GetValue()
                self.tekstboks.SetValue(f"{tekst}\n{melding}\n")
            else:
                wx.MessageBox(f"{navn} er ikke registrert.", "Feil", wx.OK | wx.ICON_ERROR)

    def slett(self, event):
        navn = wx.GetTextFromUser("Navn på venn som skal slettes:", "Slett venn")
        if navn:
            self.v.execute("DELETE FROM venner WHERE navn = ?", (navn,))
            if self.v.rowcount > 0:
                self.venner.commit()
                melding = f"Slettet venn {navn}."
            else:
                melding = f"{navn} er ikke registrert."

            tekst = self.tekstboks.GetValue()
            self.tekstboks.SetValue(f"{tekst}\n{melding}\n")

    def avslutt(self, event):
        self.venner.close()
        self.Close()

# hovedprogram
if __name__ == "__main__":
    app = wx.App(False)
    frame = Vennekontakt(None)
    app.MainLoop()