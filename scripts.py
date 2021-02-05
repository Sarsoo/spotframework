import subprocess

def test():
    """
    Run all unittests.
    """
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover', "-s", "tests"]
    )

def testv():
    """
    Run all unittests with verbose.
    """
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover', "-v", "-s", "tests"]
    )