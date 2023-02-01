import keyword
import sys


def add_debug_print(file_name, prefix):
    with open(file_name, "r") as f:
        lines = f.readlines()
    
    counter = 1
    new_lines = []
    for line in lines:
        if line.strip().startswith("def ") or line.strip().startswith("class ")\
           or line.strip().startswith("finally")\
           or line.strip().startswith("except")\
           or line.strip().startswith("else")\
            or not line.strip():
            new_lines.append(line)
            continue
        
        first_word = line.strip().split()[0]
        if keyword.iskeyword(first_word.strip()):
            new_lines.append(line)
            continue
        
        spaces = len(line) - len(line.lstrip())
        new_line = f"{' ' * spaces}print('{prefix}-py{counter}')\r\n{line}"
        new_lines.append(new_line)
        counter += 1
    
    with open(f"debug_{file_name}", "w") as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    file_name = sys.argv[1]
    
    add_debug_print(file_name, sys.argv[2] or 'A-' )
