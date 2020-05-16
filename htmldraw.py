from func import *
import subprocess
import html
import webbrowser

TAG=''

def showfile(f):
    # subprocess.Popen(['open','t.html']).wait()
    webbrowser.open(f)

def show(x):
    if isinstance(x,list): return showt(t)
    showfile(f)

def draw(s):
    with open('t.html','w') as f:
        f.write(s)
    # subprocess.Popen(['open','t.html']).wait()
    webbrowser.open('t.html')

def showt(t): draw(th(t))

def escape(x): return html.escape(str(x))

def th(t):
    if isinstance(t, str) or not isinstance(t, list):
        return escape(t)
    n = t[0]
    if isinstance(n, str):
        return f"<{n}>{''.join(map(th, t[1:]))}</{n}>"
    if isinstance(n, dict):
        tagattrs = ' '.join([n[TAG]]+[f'{a}="{escape(v)}"' for a,v in n.items() if a!=TAG])
        return f"<{tagattrs}>{''.join(map(th, t[1:]))}</{n[TAG]}>"
    print(t)
    raise ValueError

# svg=Dict[TAG:'svg', 'xmlns':"http://www.w3.org/2000/svg", 'top':0, 'width':'100%', 'left':0, 'height':'100%']
svg=Dict[TAG:'svg', 'xmlns':"http://www.w3.org/2000/svg", 'top':0, 'left':0]

def table(vv):
    return ['table']+[['tr']+[['td',x] for x in v] for v in vv]

def htmltable(vv):
    return th(table(vv))

def plain(t):
    if isinstance(t, str) or not isinstance(t, list):
        return str(t)
    n = t[0]
    if isinstance(n, str):
        if n=='i' or n=='b':
            return ' '.join(map(plain, t[1:]))
        elif n=='table':
            return plaintable(t[1:])

def trrow(tr):
    if isinstance(tr, str):
        return [tr]
    n=tr[0]
    if isinstance(n, str):
        if n=='tr':
            return tr[1:]
        else:
            return tr
    elif isinstance(n, dict):
        if n[TAG]=='tr':
            return ...

def scale(t,s):
    return [svg,[{TAG:'g', 'transform':f"scale({s})"}, t]]

def translate(t, xy):
    x,y=xy
    return [svg,[{TAG:'g', 'transform':f"translate({x},{y})"}, t]]

# >>> from htmldraw import *
# >>> 
# >>> th(['p','fred'])
# '<p>fred</p>'
# >>> th(['table',['tr',['td','one'],['td','1']],['tr',['td','two'],['td','2']],])
# '<table><tr><td>one</td><td>1</td></tr><tr><td>two</td><td>2</td></tr></table>'
# >>> table([('one','1'),('two','2')])
# ['table', ['tr', ['td', 'one'], ['td', '1']], ['tr', ['td', 'two'], ['td', '2']]]
# >>> th(_)
# '<table><tr><td>one</td><td>1</td></tr><tr><td>two</td><td>2</td></tr></table>'
## >>> draw(_)
# >>> dir(html)
# ['__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '_charref', '_html5', '_invalid_charrefs', '_invalid_codepoints', '_re', '_replace_charref', 'entities', 'escape', 'unescape']
# >>> 
# >>> th([{TAG:'p', 'align':'right'},"Word"])
# '<p align="right">Word</p>'
## >>> draw(_)
# >>> c=[svg['height':200,'width':200], [{TAG:'circle', 'cx':100, 'cy':100, 'r':90, 'stroke':'black', 'fill':'blue','stroke-width':3}]]
# >>> th(c)
# '<svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg>'
# >>> div=Dict[TAG:'div']
# >>> scale(c,2)
# [<class 'func.Lookup'>['': 'svg', 'xmlns': 'http://www.w3.org/2000/svg', 'top': 0, 'left': 0], [{'': 'g', 'transform': 'scale(2)'}, [<class 'func.Lookup'>['height': 200, 'width': 200, '': 'svg', 'xmlns': 'http://www.w3.org/2000/svg', 'top': 0, 'left': 0], [{'': 'circle', 'cx': 100, 'cy': 100, 'r': 90, 'stroke': 'black', 'fill': 'blue', 'stroke-width': 3}]]]]
# >>> th(_)
# '<svg xmlns="http://www.w3.org/2000/svg" top="0" left="0"><g transform="scale(2)"><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg></g></svg>'
# >>> # draw(_)
# >>> th(([div,[div,scale(c,2),c,scale(c,.5)],scale([div,c,c,c,c],.66)]))
# '<div><div><svg xmlns="http://www.w3.org/2000/svg" top="0" left="0"><g transform="scale(2)"><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg></g></svg><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg><svg xmlns="http://www.w3.org/2000/svg" top="0" left="0"><g transform="scale(0.5)"><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg></g></svg></div><svg xmlns="http://www.w3.org/2000/svg" top="0" left="0"><g transform="scale(0.66)"><div><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg><svg height="200" width="200" xmlns="http://www.w3.org/2000/svg" top="0" left="0"><circle cx="100" cy="100" r="90" stroke="black" fill="blue" stroke-width="3"></circle></svg></div></g></svg></div>'
# >>> # draw(_)
# >>> 
# >>> 
# >>> 
# >>> 
