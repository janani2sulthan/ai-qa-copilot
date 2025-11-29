
import subprocess
class ExecutionAgent:
    def run_pytest(self, path):
        try:
            p = subprocess.run(["pytest","-q",path],capture_output=True,text=True)
            return p.returncode, p.stdout, p.stderr
        except Exception as e:
            return 1, "", str(e)
