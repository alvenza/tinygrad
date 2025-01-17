from tinygrad.helpers import Timing
import subprocess
import multiprocessing

def _early_exec_process(qin, qout):
  while True:
    path, inp = qin.get()
    qout.put(subprocess.check_output(path, input=inp))

def enable_early_exec():
  qin: multiprocessing.Queue = multiprocessing.Queue()
  qout: multiprocessing.Queue = multiprocessing.Queue()
  p = multiprocessing.Process(target=_early_exec_process, args=(qin, qout))
  p.daemon = True
  p.start()
  def early_exec(x):
    qin.put(x)
    return qout.get()
  return early_exec

def proc(itermaker, q) -> None:
  for x in itermaker(): q.put(x)
  q.close()

def cross_process(itermaker, maxsize=8):
  # TODO: use cloudpickle for itermaker
  q: multiprocessing.Queue = multiprocessing.Queue(maxsize)
  p = multiprocessing.Process(target=proc, args=(itermaker, q))
  p.daemon = True
  p.start()

  # TODO: write tests and handle exit case
  while True: yield q.get()
