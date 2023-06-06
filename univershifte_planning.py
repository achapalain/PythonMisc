import os, random
from Framework import common


random.seed(0)


def find_latest(path):
    path = common.getFileParts(path)
    all = []
    for f in os.listdir(path[0]):
        if f.startswith(path[1]) and f.endswith(path[2]):
            all.append(path[0] + "\\" + f)
    all.sort()
    if len(all) >= 2:
        return all[-2]
    return all[-1]


programmation_path = find_latest(r"d:\Downloads\Mission équipe & bénévoles jour J.csv")
print("USING", programmation_path)
candidatures_path = find_latest(r"d:\Downloads\Candidatures - 2023.csv")
print("USING", candidatures_path)
print()


def read_csv_rows(path, remove_empty_line=True):
    text = open(path, "r", encoding="utf-8", newline="\r\n").read()
    rows = text.split("\r\n")
    for i in range(len(rows)):
        # rows[i] = rows[i].replace("\n", " ").split(";")
        rows[i] = rows[i].replace('"', "").split(";")
    if remove_empty_line:
        for i in reversed(range(len(rows))):
            is_empty = True
            for j in range(len(rows[i])):
                if rows[i][j] != '':
                    is_empty = False
            if is_empty:
                rows.pop(i)
    return rows

########################################################################################################################

TASK_ACCUEIL = [
    "Auditorium 800",
    "Auditorium 450",
    "Salle 200",
    "Salle 300",
    "Salle 150",
    "Accueil Accueil Soirée",
    "Accueil Renfort",
    "Zone Atelier / Fresque",
    "Orientation VDI",
]
TASK_MANUTENTION = [
    "Vestiaire"
]
TASK_BC = [
    "Bilan Carbone",
]
TASK_BAR = [
    "Bar",
]
ALL_TASKS = [
    TASK_ACCUEIL,
    TASK_MANUTENTION,
    TASK_BC,
    TASK_BAR,
]

INVALID_HOUR = -1

class Slot:
    def __init__(self):
        self.start_time_saturday_raw = ""
        self.start_time_saturday = INVALID_HOUR
        self.start_time_sunday_raw = ""
        self.start_time_sunday = INVALID_HOUR
        self.candidates_count = 2
        self.candidates = []
        self.candidates_left = []
        self.pre_selected_candidates = []
        self.selected_candidates = []
        self.task = ""

    def __repr__(self):
        return self.task + " " + self.start_time_saturday_raw + "h"


def get_task_index(text):
    for i in range(len(ALL_TASKS)):
        if text in ALL_TASKS[i]:
            return i


slots = []
titles = []

def load_programmation():
    rows = read_csv_rows(programmation_path)

    # Get title row
    global titles, slots
    titles = rows[0][1:]
    for i in range(len(titles)):
        titles[i] = titles[i].replace("\n", " ")

    # Find days rows
    saturday_idx, sunday_idx = 0, 0
    for i in range(len(rows)):
        if rows[i][1] == "SAMEDI":      saturday_idx = i
        elif rows[i][1] == "DIMANCHE":  sunday_idx = i

    saturday = rows[saturday_idx + 1:sunday_idx]
    sunday = rows[sunday_idx+1:]

    def time_to_hour(text):
        return int(text.split(":")[0])

    # Create slot
    for i in range(len(titles)):
        task_name = titles[i]
        if get_task_index(task_name) is None:
            continue
        sunday_starting_range = 0
        for j in range(len(saturday)):
            saturday_val = saturday[j][i+1]
            if saturday_val != '' and saturday_val.isdigit():
                slot = Slot()
                slots.append(slot)
                slot.task = task_name
                slot.candidates_count = int(saturday_val)
                slot.start_time_saturday_raw = saturday[j][0]
                slot.start_time_saturday = time_to_hour(slot.start_time_saturday_raw)
                for k in range(sunday_starting_range, len(sunday)):
                    sunday_val = sunday[k][i + 1]
                    if sunday_val != '' and sunday_val.isdigit():
                        slot.start_time_sunday_raw = sunday[k][0]
                        slot.start_time_sunday = time_to_hour(slot.start_time_sunday_raw)
                        sunday_starting_range = k + 1
                        break
                # Get pre-selected candidates
                j += 1
                while saturday[j][i+1] != '':
                    slot.pre_selected_candidates.append(saturday[j][i+1])
                    j += 1
    return

########################################################################################################################


candidates = []
candidates_left = []


class Candidate:
    def __init__(self):
        self.row = None
        self.friends = []
        self.availabilities = [[],[]]
        self.unavailability = []
        self.tasks = [0, 0, 0, 0]

    def __repr__(self):
        return self.row[COL_Prenom] + " " + self.row[COL_Nom]


COL_Caller = 0
COL_Status = COL_Caller + 1
COL_Status_orga =  COL_Status + 1
COL_Prenom = COL_Status_orga + 1
COL_Nom = COL_Prenom + 1
COL_Tel = COL_Nom + 1
COL_Mail = COL_Tel + 1
COL_TASK_Accueil = COL_Mail + 6
COL_TASK_Manutention = COL_TASK_Accueil + 1
COL_TASK_BC = COL_TASK_Manutention + 1
COL_TASK_Bar = COL_TASK_BC + 1
COL_Crenau = COL_TASK_Bar + 1
COL_Confs =COL_Crenau + 1


def load_candidates():
    rows = read_csv_rows(candidatures_path)
    # title = rows[1]
    rows = rows[2:]

    # Only keep validated candidates
    for i in reversed(range(len(rows))):
        row = rows[i]
        if row[COL_Status].lower() != "validé":
            rows.pop(i)
            continue
        c = Candidate()
        candidates.append(c)
        c.row = row

        # Get availabities
        availabilities = row[COL_Crenau].split("\n")
        # print("***", row[COL_Mail])
        for a in availabilities:
            a = a.lower().strip()
            day = -1
            if a.startswith("sam ") or a.startswith("samedi "):     day = 0
            elif a.startswith("dim ") or a.startswith("dimanche "): day = 1
            if day < 0:
                continue
            text = a[a.index(" "):].strip().replace("de", "").replace(":", "").replace("ou", ",").strip()
            tokens = text.replace("/", ",").split(",")
            for j in range(len(tokens)):
                tokens[j] = tokens[j].strip().replace("h", "").replace("00", "24")
            for t in tokens:
                try:
                    times = t.split("-")
                    start, end = int(times[0]), int(times[1])
                    for j in range(start, end):
                        c.availabilities[day].append(j)
                except:
                    # print("Unhandled", row[COL_Mail], t)
                    continue

        # Get conf/atelier availabities
        def parse_time(text):
            text = text.strip().lower()
            day_idx = -1
            if text.startswith("sam ") or text.startswith("samedi "):
                day_idx = 0
            elif text.startswith("dim ") or text.startswith("dimanche "):
                day_idx = 1
            if day_idx < 0:
                print("INVALID TIME", text)
                return
            text = text[text.index(" "):].strip().replace(":", "h")
            tokens = text.split("-")
            for i in range(len(tokens)):
                token = tokens[i]
                # Only keep first part of the time
                if "h" in token:
                    token = token[:token.index("h")]
                tokens[i] = int(token)
            return day_idx, tokens[0], tokens[1]

        confs = row[COL_Confs].split("\n")
        for l in confs:
            tokens = l.split("-")
            if len(tokens) < 4:
                continue
            conf_name = tokens[0].strip().lower()
            slot = tokens[1].strip() + "-" + tokens[2].strip()
            details = tokens[3].strip()
            day_idx, begin_hour, end_hour = parse_time(slot)
            if conf_name == "atelier" or conf_name == "fresque":
                for t in range(begin_hour, end_hour + 1):
                    if t in c.availabilities[day_idx]:
                        c.availabilities[day_idx].remove(t)
            else:
                for t in range(begin_hour, end_hour + 1):
                    if t not in c.availabilities[day]:
                        c.availabilities[day_idx].append(t)
                c.availabilities[day_idx].sort()

        def get_task_value(text):
            if text.isdigit():
                return int(text)
            return 0
        c.tasks = [
            get_task_value(row[COL_TASK_Accueil]),
            get_task_value(row[COL_TASK_Manutention]),
            get_task_value(row[COL_TASK_BC]),
            get_task_value(row[COL_TASK_Bar]),
        ]


def find_candidate_by_mail(mail):
    for c in candidates:
        if c.row[COL_Mail] == mail:
            return c


def find_candidate_by_name(name):
    name = name.lower().strip()
    for c in candidates:
        if c.row[COL_Prenom] == '' and c.row[COL_Nom] == '':
            continue
        if c.row[COL_Prenom].lower() in name and c.row[COL_Nom].lower() in name:
            return c


########################################################################################################################
def is_available(candidate, slot, logging=True):
    # Test task type
    task_index = get_task_index(slot.task)
    if task_index is None or candidate.tasks[task_index] == 0:
        return False

    # Test hours
    def test_day(hour, availabilities):
        if hour == INVALID_HOUR:
            return True
        length = len(availabilities)
        for i in range(length):
            # Ensure there is enough reserved slots
            if availabilities[i] == hour and i + 2 < length and availabilities[i + 1] == hour + 1 and availabilities[i + 2] == hour + 2:
                return True
    if not test_day(slot.start_time_saturday, candidate.availabilities[0]):
        if logging:
            print(candidate.row[COL_Mail], "not available SAMEDI for", slot.task)
        return False
    if not test_day(slot.start_time_sunday, candidate.availabilities[1]):
        if logging:
            print(candidate.row[COL_Mail], "not available DIMANCHE for", slot.task)
        return False
    return True


def validate_candidate(candidate, slot):
    if candidate not in slot.selected_candidates:
        slot.selected_candidates.append(candidate)
    global slots
    for s in slots:
        if candidate in s.candidates_left:
            s.candidates_left.remove(candidate)
    global candidates_left
    candidates_left.remove(candidate)


def process_planning(keep_pre_selected):
    global candidates_left
    candidates_left = candidates[:]
    candidates_left.sort(key=lambda x: str(x))

    # Validate current slots
    for s in slots:
        for name in s.pre_selected_candidates:
            c = find_candidate_by_name(name)
            if not c:
                print("Could not find", name)
            if not is_available(c, s, logging=False):
                print(c.row[COL_Mail], "not available for", s.task)
                continue

    # Prepare all candidates for all slots
    for s in slots:
        for c in candidates:
            if is_available(c, s, logging=False):
                s.candidates.append(c)

        # Add some randomization but keep most motivated first
        random.shuffle(s.candidates)
        task_index = get_task_index(s.task)
        for i in range(len(s.candidates)):
            c = s.candidates[i]
            if c.tasks[task_index] == 2:
                s.candidates.pop(i)
                s.candidates.insert(0, c)
        if s.candidates_count > len(s.candidates):
            print("NOT ENOUGH CANDIDATES FOR SLOT", s.task, str(s.start_time_saturday) + "h")

        # Copy to candidates left
        s.candidates_left = s.candidates[:]

    # Apply pre-validated
    if keep_pre_selected:
        for s in slots:
            for c in s.pre_selected_candidates:
                c = find_candidate_by_name(c)
                validate_candidate(c, s)

    slots_copy = slots[:]
    missing_count = [0]

    def validate_slot(slot):
        candidates_copy = slot.candidates_left[:]
        for c in candidates_copy:
            if len(slot.selected_candidates) >= slot.candidates_count:
                break
            validate_candidate(c, slot)
        if slot.candidates_count > len(slot.selected_candidates):
            missing = slot.candidates_count - len(slot.selected_candidates)
            missing_count[0] += missing
            print("COULD NOT FILL", slot.task, str(slot.start_time_saturday) + "h : ", missing)
        slots_copy.remove(slot)

    def validate_slot_target(task, hour):
        for s in slots_copy:
            if s.task == task and s.start_time_saturday == hour:
                validate_slot(s)
                return

    validate_slot_target("Bilan Carbone", 10)
    validate_slot_target("Bilan Carbone", 13)
    validate_slot_target("Bar", 18)
    validate_slot_target("Bar", 13)
    validate_slot_target("Bar", 8)
    validate_slot_target("Accueil Accueil Soirée", 17)

    # Order slots with fewer candidates count first
    slots_copy.sort(key=lambda x: len(x.candidates_left))
    slots_tmp = slots_copy[:]
    for s in slots_tmp:
        validate_slot(s)

    print("MISSING:", missing_count[0])


def print_planning():
    # # All candidates for each slot
    # print("===========================================================================================================")
    # for s in slots:
    #     print()
    #     print(s.task, str(s.start_time_saturday) + "h")
    #     if s.candidates_count > len(s.candidates):
    #         print("NOT ENOUGH CANDIDATES FOR SLOT", s.task, str(s.start_time_saturday) + "h")
    #     # print("CANDIDATES")
    #     # for c in s.candidates:
    #     #     print("\t" + c.row[COL_Prenom] + " " + c.row[COL_Nom])
    #     for c in s.selected_candidates:
    #         print("\t" + c.row[COL_Prenom] + " " + c.row[COL_Nom])

    # Unused candidate
    print("===========================================================================================================")
    global candidates_left
    for c in candidates_left:
        print("UNUSED:", c)

    # Print as table to be imported in EXCEL
    print("===========================================================================================================")
    table = []
    for t in titles:
        col = ['' for i in range(50)]
        table.append(col)
        for s in slots:
            if s.task != t:
                continue
            col_index = titles.index(s.task)
            time = s.start_time_saturday_raw.split(":")
            time = [int(time[0]), int(time[1])]
            row_index = int((time[0] - 8) * 4 + time[1] / 15)
            col[row_index] = str(s.candidates_count)
            for i in range(len(s.selected_candidates)):
                row = s.selected_candidates[i].row
                col[row_index + 1 + i] = str(s.selected_candidates[i])

    for i in range(50):
        values = []
        for j in range(len(titles)):
            values.append(table[j][i])
        print("\t".join(values))


########################################################################################################################


load_programmation()
load_candidates()
process_planning(keep_pre_selected=True)
print_planning()

