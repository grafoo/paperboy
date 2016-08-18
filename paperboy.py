#! /usr/bin/env python2

import json
import threading
import time
import urllib2
import Queue


def get_item(id=int, queue=Queue):           # type: (...) -> None
    item = json.loads(
        urllib2.urlopen(
            'https://hacker-news.firebaseio.com/v0/item/{0}.json'.format(id)).read()
    )

    tm = time.localtime(item['time'])

    try:
        queue.put({
            'time': tm,
            'score': item['score'],
            'title': item['title'].encode('utf-8'),
            'url': item['url']
        })
    except KeyError as e:
        if(e.message == 'url'):
            queue.put({
                'time': tm,
                'score': item['score'],
                'title': item['title'].encode('utf-8'),
                'url': 'https://news.ycombinator.com/item?id={0}'.format(item['id'])
            })


def get_best_stories():         # type: () -> List[int]
    return json.loads(urllib2.urlopen('https://hacker-news.firebaseio.com/v0/beststories.json').read())


def get_top_stories():          # type: () -> List[int]
    return json.loads(urllib2.urlopen('https://hacker-news.firebaseio.com/v0/topstories.json').read())


if __name__ == '__main__':
    queue = Queue.Queue()
    threads = []
    for id in get_best_stories():
        threads.append(threading.Thread(target=get_item, args=(id, queue)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    l = []
    while not queue.empty():
        l.append(queue.get())

    s = sorted(l, key=lambda x: x['score'], reverse=True)
    for i in s:
        print('{0}\n  {1}\n  {2}-{3}-{4}\n  {5}\n'.format(
            i['title'],
            i['score'],
            i['time'].tm_year,
            i['time'].tm_mon,
            i['time'].tm_mday,
            i['url']
        ))
