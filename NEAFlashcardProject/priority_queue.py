class Queue():
    def __init__(self):
        self.front = 0
        self.back = 0
        self.data = []

    def push(self, new_data, priority):
        # if queue is empty
        if len(self.data) == 0:
            self.data.append((new_data, priority))
        else:
            # compare with the priorities of all other list elements
            for i in range(len(self.data)):

                # if new priority is lower, insert to start of list
                if self.data[i][1] > priority:
                    self.data.insert(i, (new_data, priority))
                    break
                
                # if priorities are equal, insert next to each other
                elif self.data[i][1] == priority:
                    self.data.insert(i, (new_data, priority))
                    break
                else:
                    # if no position is found then append to end because new priority is the largest
                    self.data.append((new_data, priority))
                    break

    def pop(self):
        if self.front <= self.back:
            to_pop = self.data[self.front]
            self.data.remove(self.data[self.front])
            self.back = self.back - 1
            return to_pop
        else:
            print('Queue underflow')

    def peek(self):
        if self.front <= 0:
            return self.data[self.front]
        else:
            print('Queue is empty')
