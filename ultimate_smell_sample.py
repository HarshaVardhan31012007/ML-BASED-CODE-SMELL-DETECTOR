"""
ULTIMATE Code Smell Sample
Contains all 13 smells from the project taxonomy.
"""
import sqlite3
import os
import sys

# 11. GOD CLASS (> 20 methods)
class UltimateGodClass:
    def __init__(self):
        # 3. HARD-CODED CREDENTIALS
        self.db_password = "very_secret_password_123"
        self.api_token = "ABC123XYZ789TOKEN"
        self.items = []
        
    # Helper to bloat class method count
    def m1(self): pass
    def m2(self): pass
    def m3(self): pass
    def m4(self): pass
    def m5(self): pass
    def m6(self): pass
    def m7(self): pass
    def m8(self): pass
    def m9(self): pass
    def m10(self): pass
    def m11(self): pass
    def m12(self): pass
    def m13(self): pass
    def m14(self): pass
    def m15(self): pass
    def m16(self): pass
    def m17(self): pass
    def m18(self): pass
    def m19(self): pass
    def m20(self): pass
    def m21(self): pass

# 12. DEAD CODE (Defined but never used)
def unused_utility_helper():
    print("I am never called")

# 6. MISSING AUTHENTICATION (Route without login decorator)
# (Simulated for detection)
def unprotected_api_endpoint():
    # This function should have a @login_required decorator
    return "Sensitive data"

# 9. LONG METHOD (> 50 lines)
def very_long_complex_function(data, user_input):
    # 13. MAGIC STRINGS & NUMBERS
    threshold = 99.9  # Magic Number
    status = "INITIALIZING_SYSTEM_STATE" # Magic String
    
    print(status)
    print("Step 1...")
    # Procedural bloat
    a = 1; b = 2; c = 3; d = 4; e = 5; f = 6; g = 7; h = 8; i = 9; j = 10
    k = 11; l = 12; m = 13; n = 14; o = 15; p = 16; q = 17; r = 18; s = 19; t = 20
    u = 21; v = 22; w = 23; x = 24; y = 25; z = 26
    print(a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p+q+r+s+t+u+v+w+x+y+z)
    
    # 14. DEEP NESTING (> 3 levels)
    if data:
        for item in data:
            if isinstance(item, dict):
                for key in item:
                    if key == "target":
                        if item[key] > threshold:
                            print("Deep nesting reached")
                            
                            # 1. SQL INJECTION (String concat with user_input)
                            conn = sqlite3.connect("data.db")
                            # 2. UNVALIDATED INPUT / 5. MISSING SANITIZATION
                            query = "SELECT * FROM logs WHERE user='" + user_input + "'"
                            conn.execute(query)
                            
                            # 4. UNSAFE API (eval)
                            eval(user_input)
                            
                            # 7. IMPROPER ERROR HANDLING
                            try:
                                # 8. INSECURE FILE HANDLING (overly permissive/dynamic)
                                f = open(user_input + ".txt", "w+") # Permissions and dynamic
                                f.write("secret")
                                f.close()
                                os.chmod("data.db", 0o777) # Insecure permissions
                            except Exception:
                                pass # Empty except
                                
    # 10. DUPLICATE CODE (Repeated block)
    # Block A
    temp_res = 0
    for i in range(10):
        temp_res += i * threshold
    print(temp_res)
    
    # Block B (Duplicate of A)
    duplicate_res = 0
    for j in range(10):
        duplicate_res += j * threshold
    print(duplicate_res)

    # More bloat to ensure > 50 lines
    print("End of function")
    return True

if __name__ == "__main__":
    very_long_complex_function([{"target": 100}], "admin")
