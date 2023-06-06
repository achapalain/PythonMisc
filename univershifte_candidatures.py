import csv
from Framework import textParser

input_path = r"d:\Downloads\export(5).xls"

def parse_html_table_content(text):
    rows = []
    tag_row_start, tag_row_end = '<tr>', '</tr>'
    tag_header_start, tag_header_end = '<th>', '</th>'
    tag_cell_start, tag_cell_end = '<td>', '</td>'
    row_start = 0
    while row_start >= 0:
        row = []
        rows.append(row)
        row_end = text.find(tag_row_end, row_start)
        line = text[row_start + len(tag_row_start):row_end]

        # Read cells
        search_tag_start = tag_header_start if line.startswith(tag_header_start) else tag_cell_start
        search_tag_end = tag_header_end if line.startswith(tag_header_start) else tag_cell_end
        cell_start = 0
        while cell_start >= 0:
            cell_end = line.find(search_tag_end, cell_start)
            cell = line[line.find(">", cell_start) + 1:cell_end]
            row.append(cell)
            cell_start = line.find(search_tag_start, cell_end)

        # Next row
        row_start = text.find(tag_row_start, row_end)
    return rows


def read_xls_table(file_path):
    text = open(file_path, "r", encoding="utf8").read()
    if "<thead>" in text and "<tbody>" in text:
        parser = textParser.TextProc(text)
        content = parser.getBracketsContent('<thead>', "</thead>").getValue().strip()
        headers = parse_html_table_content(content)
        content = parser.getBracketsContent('<tbody>', "</tbody>").getValue().strip()
        rows = parse_html_table_content(content)
        return headers[0], rows

########################################################################################################################

class Profile:
    def __init__(self):
        self.firstname = ""
        self.surname = ""
        self.phone = ""
        self.mail = ""
        self.diet = ""
        self.why = ""
        self.availabilities = ""

TAG_mail = 0
TAG_name = 1
TAG_prénom = 2
TAG_phone = 3
TAG_diet = 4
TAG_why = 5
TAG_allergies = 6
TAG_allowCheck = 7
TAG_volunteerStatus = 8
TAG_ticket_0 = 9
TAG_ticket_1 = 10
TAG_ticket_2 = 11
TAG_ticket_3 = 12
TAG_Samedi_de_4h_à_9h = 20
TAG_Samedi_de_8h_à_12h = 15
TAG_Samedi_de_12h_à_16h = 13
TAG_Samedi_de_16h_à_20h = 16
TAG_Samedi_de_19h_à_00h = 19
TAG_Dimanche_de_8h_à_12h = 17
TAG_Dimanche_de_12h_à_16h = 14
TAG_Dimanche_de_16h_à_20h = 18
TAG_Dimanche_de_19h_à_00h = 21

removed_mails = [
    "marine.gangnebien@univershifte.fr",
    "griselda.basset@univershifte.fr",
    "sonia5_besnard@orange.fr",
]

def parse_table(headers, rows):
    for i in range(len(headers)):
        headers[i] = headers[i].replace("<b>", "").replace("</b>", "")
    profiles = []
    tickets = []
    for row in rows:
        p = Profile()
        profiles.append(p)

        # General
        p.firstname = row[TAG_prénom].strip()
        p.surname = row[TAG_name].strip()
        p.mail = row[TAG_mail].strip()
        p.why = row[TAG_why].strip()
        p.diet = (row[TAG_diet].strip() + "\n" + row[TAG_allergies].strip()).strip()

        # Phone
        p.phone = row[TAG_phone].strip()
        p.phone = p.phone.replace("+33", "0").replace(".", "").replace(" ", "").replace("-", "")
        if p.phone.startswith("00"):
            p.phone = p.phone[1:]
        if len(p.phone) != 10 and len(p.phone) != 0:
            print("UNHANDLED Phone number: " + row[TAG_phone].strip())
        else:
            for i in reversed(range(4)):
                p.phone = p.phone[:2 * i + 2] + " " + p.phone[2 * i + 2:]

        # Availability
        time_cells = [[-1, 100]]
        def check_duration(tag_time, _start, _end):
            if row[tag_time] == "true":
                if time_cells[-1][0] < 0:
                    time_cells[-1][0] = _start
                elif _start > time_cells[-1][1]:
                    time_cells.append([_start, _end])
                time_cells[-1][1] = _end
        check_duration(TAG_Samedi_de_4h_à_9h, 4, 9)
        check_duration(TAG_Samedi_de_8h_à_12h, 8, 12)
        check_duration(TAG_Samedi_de_12h_à_16h, 12, 16)
        check_duration(TAG_Samedi_de_16h_à_20h, 16, 20)
        check_duration(TAG_Samedi_de_19h_à_00h, 19, 24)
        saturday = ""
        for cell in time_cells:
            if cell[0] != -1:
                saturday += "\nSam " + str(cell[0]) + "h-" + str(cell[1]) + "h"

        time_cells = [[-1, 100]]
        check_duration(TAG_Dimanche_de_8h_à_12h, 8, 12)
        check_duration(TAG_Dimanche_de_12h_à_16h, 12, 16)
        check_duration(TAG_Dimanche_de_16h_à_20h, 16, 20)
        check_duration(TAG_Dimanche_de_19h_à_00h, 19, 24)
        sunday = ""
        for cell in time_cells:
            if cell[0] != -1:
                saturday += "\nDim " + str(cell[0]) + "h-" + str(cell[1]) + "h"
        p.availabilities = (saturday + "\n" + sunday).strip()

        # Tickets
        if row[TAG_ticket_0] not in tickets: tickets.append(row[TAG_ticket_0])
        if row[TAG_ticket_1] not in tickets: tickets.append(row[TAG_ticket_1])
        if row[TAG_ticket_2] not in tickets: tickets.append(row[TAG_ticket_2])
        if row[TAG_ticket_3] not in tickets: tickets.append(row[TAG_ticket_3])

    return profiles


def print_profiles(profiles):
    cells_format = '{}\t{}\t{}\t{}\t\t\t\t\t{}\t\t\t\t\t"{}"\t\t"{}"'
    print(cells_format.format("Prénom", "Nom", "Tel", "Mail", "Why", "Dispos", "Régime"))
    for p in profiles:
        if p.mail in removed_mails:
            continue
        print(cells_format.format(p.firstname, p.surname, p.phone, p.mail, p.why, p.availabilities, p.diet))


headers, rows = read_xls_table(input_path)
profiles = parse_table(headers, rows)
print_profiles(profiles)