"""Quick test for the name extraction fix (periods in names)."""
import sys
sys.path.insert(0, "D:\\PROJECTS\\Final project\\AI Interview Intelligence System")
from resume_parser import extract_name

def test_period_in_names():
    # Case 1: Title with period
    name = extract_name("Dr. Maya Patel\nSoftware Engineer\n...")
    print(f"1. 'Dr. Maya Patel'      -> '{name}'")
    assert name and ("Dr." in name or "Maya" in name), f"FAIL: got '{name}'"
    # Case 2: Initial with period, uppercase
    name = extract_name("J. ROBERT SMITH\nProduct Manager\n...")
    print(f"2. 'J. ROBERT SMITH'     -> '{name}'")
    assert name != "", f"FAIL: got empty string"
    # Case 3: Plain name, no dots
    name = extract_name("Alex Chen\nDeveloper\n...")
    print(f"3. 'Alex Chen'           -> '{name}'")
    assert name == "Alex Chen", f"FAIL: got '{name}'"
    # Bonus: rejects section headings / junk
    name = extract_name("TECHNICAL SKILLS\n>>>> about me <<<<\n...")
    print(f"4. Section heading       -> '{name}'")
    assert name == "", f"FAIL: should reject section heading, got '{name}'"

if __name__ == "__main__":
    test_period_in_names()
    print("\nAll tests passed!")
