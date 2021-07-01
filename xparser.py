class Flag:
    def __init__(self, value, attr_set=None):
        self.value = value
        self.set = attr_set

class Modifier:
    def __init__(self, id, diff):
        self.id = id
        self.diff = diff

class Outcome:
    def __init__(self, mods, flags,
            prob=1.0, text='sample outcome txt'):
        self.modifiers = mods if len(mods)>0 else list()
        self.flags = flags if len(flags)>0 else list()
        self.prob = prob
        self.text = text

class Option:
    def __init__(self,
            outcomes,
            name='default name', text="default text"):
        self.outcomes = outcomes if len(outcomes)>0 else list()
        self.name = name
        self.text = text

class Event:
    def __init__(self,
            options, flags,
            name='default evnt', text='default evnt txt',
            ):
        self.options = options if len(options)>0 else list()
        self.flags = flags if len(flags)>0 else list()
        self.name = name
        self.text = text

    def __str__(self):
        return f'{self.name}, {self.text}, opts: {[opt.name for opt in self.options]}'

def starts_with(line, word):
    return word in line and line.index(word) == 0

def parse_string(f, line, strOpen=False):
    result = ''
    for ch in line:
        if ch == "'":
            strOpen = not strOpen
            continue
        if strOpen:
            result += ch
    if strOpen:
        result += parse_string(f, ' ' + f.readline().strip(), True)
    return result

def parse_flag(f, line):
    flagVal = parse_string(f, line)
    setAttr = None
    while(line := f.readline()):
        linelen = len(line)
        line = line.strip()
        if starts_with(line, 'set'):
            setAttr = parse_string(f, line)
        else:
            f.seek(f.tell() - linelen)
            break
    return Flag(flagVal, setAttr)

def parse_mod(f):
    modId = ''
    modDiff = ''
    while(line := f.readline()):
        linelen = len(line)
        line = line.strip()
        if starts_with(line, 'id'):
            modId = parse_string(f, line)
        elif starts_with(line, 'diff'):
            modDiff = parse_string(f, line)
        else:
            f.seek(f.tell() - linelen)
            break
    return Modifier(modId, modDiff)

def parse_outcome(f):
    prob = ''
    outcomeText = ''
    mods = []
    outcomeFlags = []
    while(line := f.readline()):
        linelen = len(line)
        line = line.strip()
        if starts_with(line, 'prob'):
            prob = parse_string(f, line)
        elif starts_with(line, 'text'):
            outcomeText = parse_string(f, line)
        elif starts_with(line, 'flag'):
            outcomeFlags.append(parse_flag(f, line))
        elif starts_with(line, 'mod'):
            mods.append(parse_mod(f))
        else:
            f.seek(f.tell() - linelen)
            break
    return Outcome(mods, outcomeFlags, prob, outcomeText)

def parse_opt(f):
    optName = ''
    optText = ''
    outcomes = []
    while(line := f.readline()):
        linelen = len(line)
        line = line.strip()
        if starts_with(line, 'name'):
            optName = parse_string(f, line)
        elif starts_with(line, 'text'):
            optText = parse_string(f, line)
        elif starts_with(line, 'outcome'):
            outcomes.append(parse_outcome(f))
        else:
            f.seek(f.tell() - linelen)
            break
    return Option(outcomes, optName, optText)

def parse_event(f):
    name = ''
    text = ''
    options = []
    flags = []
    while(line := f.readline()):
        linelen = len(line)
        line = line.strip()
        if starts_with(line, 'name'):
            name = parse_string(f, line)
        elif starts_with(line, 'text'):
            text = parse_string(f, line)
        elif starts_with(line, 'flag'):
            flags.append(parse_flag(f, line))
        elif starts_with(line, 'opt'):
            options.append(parse_opt(f))
        elif starts_with(line, 'event'):
            f.seek(f.tell() - linelen)
            break
    return Event(options, flags, name, text)

def parse(filename):
    events = []
    with open(filename, 'r') as f:
        while(line := f.readline()):
            linelen = len(line)
            line = line.strip()
            if 'event' in line and line.index('event') == 0:
                events.append(parse_event(f))
    return events

def makeXML(events, filename='out.xml'):
    with open(filename, 'w') as outfile:
        outfile.write('<events>\n')
        for event in events:
            outfile.write(f'\t<event Name="{event.name}">\n')
            outfile.write(f'\t\t<text>{event.text}</text>\n')
            for flag in event.flags:
                openTag = '<flag>' if not flag.set else f'<flag Set="{flag.set}">'
                outfile.write(f'\t\t{openTag}{flag.value}</flag>\n')
            for opt in event.options:
                outfile.write(f'\t\t<option Name="{opt.name}">\n')
                outfile.write(f'\t\t\t<text>{opt.text}</text>\n')
                for outcome in opt.outcomes:
                    outfile.write(f'\t\t\t<outcome Probability="{outcome.prob}">\n')
                    outfile.write(f'\t\t\t\t<text>{outcome.text}</text>\n')
                    for flag in outcome.flags:
                        openTag = '<flag>' if not flag.set else f'<flag Set="{flag.set}">'
                        outfile.write(f'\t\t\t\t{openTag}{flag.value}</flag>\n')
                    outfile.write(f'\t\t\t\t<modifiers>\n')
                    for mod in outcome.modifiers:
                        outfile.write(f'\t\t\t\t\t<modifier Resource="{mod.id}">{mod.diff}</modifier>\n')
                    outfile.write(f'\t\t\t\t</modifiers>\n')
                    outfile.write(f'\t\t\t</outcome>\n')
                outfile.write(f'\t\t</option>\n')
            outfile.write('\t</event>\n')
        outfile.write('</events>\n')


def main():
    filename = argv[1]
    new_file_name = path.splitext(path.basename(filename))[0] + '.xml'
    events = parse(filename)
    makeXML(events, new_file_name)

if __name__ == '__main__':
    from sys import argv
    from os import path
    if len(argv) > 1:
        main()
    else:
        print('please supply source file path as command line argument')

'''
example input file:

event
    name='event 1'
    text='multiline desc
      line2
      line3'
    flag='opt 1 flag'
    opt
        name='yes'
        text='yes opt text'
        outcome
            flag='outcome 1 flag'
              set='true'
            prob='0.5'
            text='outcome 1 to yes'
            mod
              id='Legality'
              diff='-1'
            mod
              id='Revenue'
              diff='5'
        outcome
            prob='0.5'
            text='outcome 2 to yes'
            mod
              id='Legality'
              diff='-1'
    opt
        name='no'
        text='no opt text'
        outcome
            prob='1.0'
            text='outcome to no'
            mod
              id='Legality'
              diff='1'
'''
