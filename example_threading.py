import threading, requests as rq

total_threads = 10
link = "http://www.google.com"
def req(link):
  r = rq.get(link)
  return r.status_code
threads = list()
for index in range(1,total_threads):
  currentThread = threading.Thread(target=req,args=(link))
  threads.append(currentThread)
  currentThread.start()
