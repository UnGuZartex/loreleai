class SearchStats:

    def __init__(self, stopped_early, ex_time, exp_len, exp_count, max_queue_len, rules):
        self.stopped_early = stopped_early
        self.ex_time = ex_time
        self.exp_len = exp_len
        self.exp_count = exp_count
        self.max_queue_len = max_queue_len
        self.rules = rules

        self.nn_amount = 0
        self.task = ""

    def set_task(self, task):
        self.task = task

    def set_nn_amount(self, nn_amount):
        self.nn_amount = nn_amount

    def __str__(self):
        return "------------------------------\n" + \
               "TASK: " + self.task + "\n" + \
               "FILTER SIZE: " + str(self.nn_amount) + "\n" + \
               "TIME: " + str(self.ex_time) + "\n" + \
               "STOPPED EARLY: " + str(self.stopped_early) + "\n" + \
               "EXP LEN: " + str(self.exp_len) + "\n" + \
               "EXP COUNT: " + str(self.exp_count) + "\n" + \
               "MAX QUEUE LEN: " + str(self.max_queue_len) + "\n" + \
               "RULES: " + str(self.rules) + "\n" + \
               "------------------------------\n"
