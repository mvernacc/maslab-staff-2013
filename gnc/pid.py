import time

class PIDController:
    def __init__(self, k_P, k_I, k_D, target_value = 0):
        self.k_P = k_P
        self.k_I = k_I
        self.k_D = k_D
        self.e_P = 0
        self.e_I = 0
        self.e_D = 0
        self.target_value = target_value
        self.adjusted_value = target_value
        self.last_time = None
    def send_value(self, value):
        # Check for first run
        if self.last_time == None:
            self.last_time = time.time()
            self.e_P = value - self.target_value
            return
        # Update the time difference
        new_time = time.time()
        dt = new_time - self.last_time
        self.last_time = new_time
        # Update the errors
        new_error = value - self.target_value
        self.e_D = (new_error - self.e_P) / dt
        self.e_I += new_error * dt
        self.e_P = new_error
        # Update the adjusted value
        self.adjusted_value = self.target_value - (self.k_P * self.e_P + self.k_I * self.e_I + self.k_D * self.e_D)
