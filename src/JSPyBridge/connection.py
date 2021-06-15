import threading, subprocess, json, time, signal
import atexit, os
from .config import debug

# Currently this uses process standard input & standard error pipes
# to communicate with JS, but this can be turned to a socket later on

dn = os.path.dirname(__file__)

try:
    proc = subprocess.Popen(
        ["node", dn + "/js/bridge.js"],
        stdin=subprocess.PIPE,
        # stdout=self.stdout,
        stderr=subprocess.PIPE
        # shell=True
    )
except Exception as e:
    # v = subprocess.check_output(['npm', 'version'])
    # print(v.decode())
    print(
        "--====--\t--====--\n\nBridge failed to spawn JS process!\n\nDo you have Node.js 15 or newer installed? Get it at https://nodejs.org/\n\n--====--\t--====--"
    )
    raise e


def read_stderr(stderrs):
    ret = []
    for stderr in stderrs:
        inp = stderr.decode("utf-8")
        for line in inp.split("\n"):
            if not len(line):
                continue
            try:
                d = json.loads(line)
                debug("[js -> py]", int(time.time() * 1000), line)
                ret.append(d)
            except ValueError as e:
                print("[JSE]", line)
    return ret


# Run a remote command and then wait for the outcome
def exec_sync(command, timeout=1000):
    if type(command) is str:
        j = command
    else:
        j = json.dumps(command)
    time.sleep(1)
    debug("[py -> js]", int(time.time() * 1000), j)
    stdout, stderr = proc.communicate(input=j.encode(), timeout=2)
    print(stdout, stderr)
    ret = []

    return read_stderr(stderr)


# Run a remote command, and wait for outcome that matches request_id
# Since we can be multitasking over the same pipe, it's possible exec_sync
# will run but with output for a different command.
def command(requestId, command, pollingInterval=20):
    for line in exec_sync(command):
        if line["r"] == requestId:
            return line
    return None


# Write a message to a remote socket, in this case it's standard input
# but it could be a websocket (slower) or other generic pipe.
def writeAll(objs):
    for obj in objs:
        j = json.dumps(obj) + "\n"
        debug("[py -> js]", int(time.time() * 1000), j)
        proc.stdin.write(j.encode())
        proc.stdin.flush()


stderr_lines = []

# Reads from the socket, in this case it's standard error. Returns an array
# of responses from the server.
def readAll():
    ret = read_stderr(stderr_lines)
    stderr_lines.clear()
    return ret


def com_io():
    while proc.poll() == None:
        stderr_lines.append(proc.stderr.readline())


com_thread = threading.Thread(target=com_io, args=(), daemon=True)
com_thread.start()


def kill_proc():
    proc.terminate()


# Make sure out child process is killed if the parent one is exiting
atexit.register(kill_proc)

# print("Got", command(100, { "r": 100, "ffid": 0, "action": "get", "key": "console" }))