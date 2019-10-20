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


# print(get_vote_ext_from_num(-124))
# print(get_vote_ext_from_num(0))
# print(get_vote_ext_from_num(1))
# print(get_vote_ext_from_num(81))
# print(get_vote_ext_from_num(171))
# print(get_vote_ext_from_num(325))
# print(get_vote_ext_from_num(326))
# print(get_vote_ext_from_num(631782))

def print_lines(lines):
    [print(l) for l in lines]

def print_vote(description, tuple):
    print(description)
    for t in tuple:
        print_lines(t)
        print()


def fetch_page_as_lines(url):
    fp = urllib.request.urlopen(url)
    my_str = fp.read().decode("utf8")
    fp.close()
    lines = my_str.split("\n")
    return lines


def filter_feed_old(lines):
    to_ret = []
    write_flag = False
    for l in lines:
        if "<span class=\"contenttext\">" in l:
            write_flag = True
        if write_flag:
            to_ret.append(l)
        if "</span>" in l:
            write_flag = False
    return to_ret


def filter_feed(lines):
    to_ret = []
    last_line = ""
    for l in lines:
        if "</span>" in l and "<span class=\"contenttext\">" in last_line:
            to_ret.append(last_line)
        last_line = l
    return to_ret

def get_yays(filtered_lines):
    yays = filtered_lines[0].split("<br>")
    yays[0] = yays[0][26:]
    return yays

def get_nays(filtered_lines):
    nays = filtered_lines[1].split("<br>")
    nays[0] = nays[0][26:]
    return nays

def get_miss(filtered_lines):
    miss = filtered_lines[2].split("<br>")
    miss[0] = miss[0][26:]
    return miss


def votes_from_url(url):
    lines = fetch_page_as_lines(url)
    filter_lines = filter_feed(lines)
    yays = get_yays(filter_lines)
    nays = get_nays(filter_lines)
    miss = get_miss(filter_lines)
    return yays, nays, miss

vote_history = {0: {"yays": [], "nays": [], "miss": []}}
senator_history = {"senator": {"yays": [0], "nays": [], "miss": []}}
def write_to_history(vote_num, vote_tupe):
    vote_history[vote_num] = {"yays": vote_tupe[0], "nays": vote_tupe[1], "miss": vote_tupe[2]}
    for yay_voter in vote_tupe[0]:
        if yay_voter not in senator_history:
            senator_history[yay_voter] = {"yays": [], "nays": [], "miss": []}
        senator_history[yay_voter]["yays"].append(vote_num)
    for nay_voter in vote_tupe[1]:
        if nay_voter not in senator_history:
            senator_history[nay_voter] = {"yays": [], "nays": [], "miss": []}
        senator_history[nay_voter]["nays"].append(vote_num)
    for missed_voter in vote_tupe[2]:
        if missed_voter not in senator_history:
            senator_history[missed_voter] = {"yays": [], "nays": [], "miss": []}
        senator_history[missed_voter]["miss"].append(vote_num)

print(vote_history)
vote = votes_from_url(url_base + get_vote_ext_from_num(125))
# print_vote("Vote 125:", vote)
write_to_history(125, vote)
print(vote_history)

vote = votes_from_url(url_base + get_vote_ext_from_num(291))
# print_vote("Vote 291:", vote)
write_to_history(291, vote)
print(vote_history)
