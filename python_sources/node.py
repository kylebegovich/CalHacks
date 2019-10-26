class Node:
    def __init__(self, title, data):
        self.title = title
        self.data = data

    def get_keys(self):
        pass

    def get_data(self):
        pass

    def get_csv(self):
        pass


class SenatorNode(Node):
    def __init__(self, title, senators, max_vote_index):
        self.title = title
        self.data = dict([(s, {}) for s in senators])  # maps of senator names to vote_id: vote map
        self.sorted_keys = sorted(list(self.data.keys()))
        self.max_vote = max_vote_index
        self.csv = ""

    def get_keys(self):
        return self.data.keys()

    def get_data(self):
        return self.data

    def get_key_data(self, key):
        return self.data[key]

    def get_sorted_keys(self):
        return self.sorted_keys

    def get_csv(self):
        if self.csv == "":
            self.csv = "VoteNumber," + ",".join(self.data.keys()) + "\n"
        return self.csv

    def add_vote(self, vote_id, vote_data):
        print("add_vote")
        self.max_vote += 1
        list_to_append = [""] * 101
        list_to_append[0] = str(vote_id)
        for yea_voter in vote_data[0]:
            if yea_voter != "":
                self.data[yea_voter][vote_id] = "YEA"
        for nay_voter in vote_data[1]:
            if nay_voter != "":
                self.data[nay_voter][vote_id] = "NAY"
        for missed_voter in vote_data[2]:
            if missed_voter != "":
                self.data[missed_voter][vote_id] = "Not Voting"

        vote_line =  [f"{vote_id}"]
        print("vote_line")
        for senator in self.sorted_keys:
            vote_line.append(self.data[senator][vote_id])
        self.csv += (",".join(vote_line) + "\n")
