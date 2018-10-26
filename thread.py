#!/usr/bin/env python
import threading
import sys
import requests

# url = "http://media.mnn.com/assets/images/2018/07/cat_eating_fancy_ice_cream.jpg.838x0_q80.jpg"


def split_url_list(urls, num):
    ret = [[] for x in range(num)]

    for x in range(len(urls)):
        ret[x % num].append(urls[x])

    return filter(lambda l: len(l) > 0, ret)


def runner(progress, files, printing=False):
    if printing:
        progress[3] = len(files)

    for f_name in files:
        r = requests.get(f_name, stream=True)
        local_filename = f_name.split('/')[-1]
        if printing:
            progress[2] += 1
            progress[1] = local_filename
            size_max = r.headers['Content-Length']
            size_dl = 0
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    if printing:
                        size_dl += len(chunk)
                        progress[0] = float(size_dl) / float(size_max) * 100
                    f.write(chunk)

    return


def up():
    sys.stdout.write('\x1b[1A')
    sys.stdout.flush()


def progress_print(p):

    for x in p:
        print()

    while threading.active_count() > 2:
        string = ""
        for x in p:
            up()
        for x in range(len(p)):
            string += "[%-20s] %.2f | %s | (%d of %d)\n" % (
                                                '=' * (int(p[x][0]/5)-1) + '>',
                                                float(p[x][0]),
                                                p[x][1] if p[x][1] else "",
                                                p[x][2],
                                                p[x][3])

        sys.stdout.write(string)
        sys.stdout.flush()


if __name__ == "__main__":
    threads = []
    num = 1
    printing = False

    if '-t' in sys.argv:
        try:
            print(sys.argv[sys.argv.index('-t') + 1])
            num = int(sys.argv[sys.argv.index('-t') + 1])
        except Exception as e:
            print("Error trying to parse thread count | option: -t")
            exit(1)

    files = []

    for line in sys.stdin:
        files.append(line.strip())

    files = split_url_list(files, num)

    # make sure we don't spawn additional threads
    if len(files) < num:
        num = len(files)

    progress = [[0, None, 0, 0] for x in range(num)]

    if '-v' in sys.argv:
        printing = True
        threads.append(threading.Thread(target=progress_print,
                                        args=(progress,)))
                                        
    for x in range(num):
        threads.append(threading.Thread(target=runner,
                                        args=(progress[x],
                                              files[x],
                                              printing)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
