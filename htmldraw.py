import subprocess
import html
import webbrowser

def draw(s):
    with open('t.html','w') as f:
        f.write(s)
    # subprocess.Popen(['open','t.html']).wait()
    webbrowser.open('t.html')

def show(t): draw(th(t))

def th(t):
    if isinstance(t, str) or not isinstance(t, list):
        return html.escape(str(t))
    n = t[0]
    if isinstance(n, str):
        return f"<{n}>{''.join(map(th, t[1:]))}</{n}>"
    if isinstance(n, dict):
        tagattrs = ' '.join([n['tag']]+[f'{a}="{v}"' for a,v in n if a!='tag'])
        return f"<{tagattrs}>{''.join(map(th, t[1:]))}</{n['tag']}>"
    print(t)
    raise ValueError

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
        if n['tag']=='tr':
            return ...


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
# >>> 
