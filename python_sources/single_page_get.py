import urllib.request


url_stripped = "https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm"
current_session_url_ext = "?congress=116&session=1"
url_base = url_stripped + current_session_url_ext
url_example = "https://www.senate.gov/legislative/LIS/roll_call_lists/roll_call_vote_cfm.cfm?congress=116&session=1&vote=00325"

VOTE_NUM_MAX = 325
VOTE_STR = "vote="
def get_vote_ext_from_num(vote_number):
    if vote_number > VOTE_NUM_MAX or vote_number < 1:
        return ""
    if vote_number > 99:
        return "&" + VOTE_STR + "00" + str(vote_number)
    if vote_number > 9:
        return "&" + VOTE_STR + "000" + str(vote_number)
    return "&" + VOTE_STR + "0000" + str(vote_number)


def print_lines(lines):
    [print(l) for l in lines]

def print_vote(description, tuple):
    print(description)
    for t in tuple:
        print_lines(t)
        print()

def print_vote_history():
    for k, v in vote_history.items():
        print(k)
        print("yeas")
        [print(sen) for sen in v["yeas"]]
        print("nays")
        [print(sen) for sen in v["nays"]]
        print("miss")
        [print(sen) for sen in v["miss"]]

def print_sen_history():
    for k, v in senator_history.items():
        print(k)
        print("yeas")
        [print(vote) for vote in v["yeas"]]
        print("nays")
        [print(vote) for vote in v["nays"]]
        print("miss")
        [print(vote) for vote in v["miss"]]

def get_state_color_map_from_vote(vote_num):
    return [(str(k) + "," + str(v)) for k, v in vote_state_history[vote_num].items()]

def fetch_page_as_lines(url):
    fp = urllib.request.urlopen(url)
    my_str = fp.read().decode("utf8")
    fp.close()
    lines = my_str.split("\n")
    return lines

def filter_feed(lines):
    to_ret = []
    last_line = ""
    for l in lines:
        if "</span>" in l and "<span class=\"contenttext\">" in last_line:
            to_ret.append(last_line)
        last_line = l
    return to_ret

def get_yeas(filtered_lines, index):
    yeas = filtered_lines[index].split("<br>")
    yeas[0] = yeas[0][26:]
    return yeas

def get_nays(filtered_lines, index):
    nays = filtered_lines[index].split("<br>")
    nays[0] = nays[0][26:]
    return nays

def get_miss(filtered_lines, index):
    miss = filtered_lines[index].split("<br>")
    miss[0] = miss[0][26:]
    return miss

def parse_ynm(lines, filter_lines):
    if len(filter_lines) == 3:
        yeas = get_yeas(filter_lines, 0)
        nays = get_nays(filter_lines, 1)
        miss = get_miss(filter_lines, 2)
        return yeas, nays, miss

    is_yeas = False
    is_nays = False
    is_miss = False
    for l in lines:
        if "YEAs ---" in l:
            is_yeas = True
        if "NAYs ---" in l:
            is_nays = True
        if "Not Voting -" in l:
            is_miss = True
    yeas = []
    nays = []
    miss = []
    if is_yeas:
        yeas = get_yeas(filter_lines, 0)
        if is_nays:
            nays = get_nays(filter_lines, 1)
        else:
            if is_miss:
                miss = get_miss(filter_lines, 1)
    else:
        if is_nays:
            nays = get_nays(filter_lines, 0)
            if is_miss:
                miss = get_miss(filter_lines, 1)
        else:
            if is_miss:
                miss = get_miss(filter_lines, 0)
    return yeas, nays, miss

def votes_from_url(url):
    lines = fetch_page_as_lines(url)
    filter_lines = filter_feed(lines)
    return parse_ynm(lines, filter_lines)

def get_senators():
    y, n, m = votes_from_url(url_example)
    senators = []
    for sen in y:
        senators.append(sen)
    for sen in n:
        senators.append(sen)
    for sen in m:
        senators.append(sen)
    senators = sorted(list(set(senators)))
    return senators[1:]

def get_state_from_senator(senator):
    return senator[-3:-1]

table_map = {}

def init_table():
    senators = get_senators()
    index = 1
    for sen in senators:
        table_map[sen] = index
        index += 1

    table_header = ["Vote Number"]
    [table_header.append(sen) for sen in senators]
    return [table_header]


vote_history = {}  # ex: 125: {"yeas": ["sen1"], "nays": ["sen2"], "miss": []}
senator_history = {}  # ex: "senator": {"yeas": [125], "nays": [62], "miss": []}
vote_state_history = {}  # ex: 125: {"TN": "red", "IL": "blue", "PN": "purple" ...}
vote_senator_table_history = init_table()

def write_to_vote_state_history(vote_num, vote_tupe):
    state_votes = {}
    for yea_voter in vote_tupe[0]:
        if yea_voter == "":
            continue
        state = get_state_from_senator(yea_voter)
        if state not in state_votes:
            state_votes[state] = float(2)
        state_votes[state] += 1
    for nay_voter in vote_tupe[1]:
        if nay_voter == "":
            continue
        state = get_state_from_senator(nay_voter)
        if state not in state_votes:
            state_votes[state] = float(2)
        state_votes[state] -= 1
    for missed_voter in vote_tupe[2]:
        if missed_voter == "":
            continue
        state = get_state_from_senator(missed_voter)
        if state not in state_votes:
            state_votes[state] = float(2)

    vote_state_history[vote_num] = state_votes

def write_to_history(vote_num, vote_tupe):
    write_to_vote_state_history(vote_num, vote_tupe)
    vote_history[vote_num] = {"yeas": vote_tupe[0], "nays": vote_tupe[1], "miss": vote_tupe[2]}
    list_to_append = [""] * 101
    list_to_append[0] = str(vote_num)
    for yea_voter in vote_tupe[0]:
        if yea_voter not in senator_history:
            senator_history[yea_voter] = {"yeas": [], "nays": [], "miss": []}
        if yea_voter != "":
            senator_history[yea_voter]["yeas"].append(vote_num)
            list_to_append[table_map[yea_voter]] = "YEA"
    for nay_voter in vote_tupe[1]:
        if nay_voter not in senator_history:
            senator_history[nay_voter] = {"yeas": [], "nays": [], "miss": []}
        if nay_voter != "":
            senator_history[nay_voter]["nays"].append(vote_num)
            list_to_append[table_map[nay_voter]] = "NAY"
    for missed_voter in vote_tupe[2]:
        if missed_voter not in senator_history:
            senator_history[missed_voter] = {"yeas": [], "nays": [], "miss": []}
        if missed_voter != "":
            senator_history[missed_voter]["miss"].append(vote_num)
            list_to_append[table_map[missed_voter]] = "Not Voting"
    vote_senator_table_history.append(list_to_append)


# vote = votes_from_url(url_base + get_vote_ext_from_num(125))
# write_to_history(125, vote)
#
# vote = votes_from_url(url_base + get_vote_ext_from_num(291))
# write_to_history(291, vote)

# vote = votes_from_url(url_base + get_vote_ext_from_num(1))
# print_vote("Vote 1:", vote)
# write_to_history(315, vote)


# [print(l) for l in fetch_page_as_lines(url_base + get_vote_ext_from_num(315))]
#

# # print_vote_history()
# # print()
# # print()
# # print_sen_history()
# print_sen_history_csv()
# [print(l) for l in vote_senator_table_history]


#
# for i in range(31):
#     print(",".join(vote_senator_table_history[i]))

# from node import SenatorNode
#
# SenateNode = SenatorNode("Senate to voting record", get_senators(), 0)
#
# print(SenateNode.get_csv())
# for i in range(1, 11):
#     vote = votes_from_url(url_base + get_vote_ext_from_num(i))
#     SenateNode.add_vote(i, vote)
#     print(SenateNode.get_csv())

# vote = votes_from_url(url_base + get_vote_ext_from_num(1))
# SenateNode.add_vote(1, vote)
# print(SenateNode.get_csv())

# print()

vote = votes_from_url(url_base + get_vote_ext_from_num(1))
# print_vote("Vote 1:", vote)
write_to_history(1, vote)
# print(vote_state_history)
# print()
# print(vote_state_history[1])
# print()
print("state,color")
[print(line) for line in get_state_color_map_from_vote(1)]
